//+------------------------------------------------------------------+
//|                                         PythonBridge_MT5.mq5     |
//|                                   Python Trading Bot Bridge      |
//|                                   MetaTrader 5 Expert Advisor    |
//+------------------------------------------------------------------+
#property copyright "Trading Bot Bridge"
#property link      ""
#property version   "1.00"
#property strict

//--- Input parameters
input string   PythonHost = "127.0.0.1";      // Python server IP
input int      PythonPort = 9090;             // Python server port
input string   TradingSymbol = "";            // Symbol (empty = current chart)
input int      MagicNumber = 234000;          // Magic number for orders
input bool     EnableAutoTrading = true;      // Enable auto trading
input int      HeartbeatSeconds = 5;          // Heartbeat interval

//--- Global variables
int socketHandle = INVALID_HANDLE;
datetime lastHeartbeat;
string currentSymbol;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("=== Python Bridge MT5 EA Starting ===");
   
   // Set symbol
   if(TradingSymbol == "")
      currentSymbol = Symbol();
   else
      currentSymbol = TradingSymbol;
   
   Print("Symbol: ", currentSymbol);
   Print("Python Server: ", PythonHost, ":", PythonPort);
   Print("Magic Number: ", MagicNumber);
   
   // Don't fail if Python not connected yet - will retry on tick
   Print("⚠️  Will attempt to connect to Python on first tick");
   Print("✅ EA Initialized - Waiting for Python connection...");
   
   lastHeartbeat = TimeCurrent();
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("=== Python Bridge MT5 EA Stopping ===");
   
   if(socketHandle != INVALID_HANDLE)
   {
      SocketClose(socketHandle);
      socketHandle = INVALID_HANDLE;
   }
   
   Print("Disconnected from Python");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Check connection, try to reconnect if needed
   if(socketHandle == INVALID_HANDLE)
   {
      // Try to connect every 10 seconds
      static datetime lastConnectAttempt = 0;
      if(TimeCurrent() - lastConnectAttempt >= 10)
      {
         Print("Attempting to connect to Python...");
         if(ConnectToPython())
         {
            Print("✅ Connected to Python successfully");
         }
         else
         {
            Print("⚠️  Connection failed, will retry in 10 seconds");
         }
         lastConnectAttempt = TimeCurrent();
      }
      return;
   }
   
   // Send market data on every tick
   SendMarketData();
   
   // Check for Python commands
   CheckPythonCommands();
   
   // Heartbeat
   if(TimeCurrent() - lastHeartbeat >= HeartbeatSeconds)
   {
      SendHeartbeat();
      lastHeartbeat = TimeCurrent();
   }
}

//+------------------------------------------------------------------+
//| Connect to Python server                                         |
//+------------------------------------------------------------------+
bool ConnectToPython()
{
   socketHandle = SocketCreate();
   if(socketHandle == INVALID_HANDLE)
   {
      Print("ERROR: Failed to create socket");
      return false;
   }
   
   if(!SocketConnect(socketHandle, PythonHost, PythonPort, 1000))
   {
      Print("ERROR: Failed to connect to ", PythonHost, ":", PythonPort);
      SocketClose(socketHandle);
      socketHandle = INVALID_HANDLE;
      return false;
   }
   
   return true;
}

//+------------------------------------------------------------------+
//| Send market data to Python                                       |
//+------------------------------------------------------------------+
void SendMarketData()
{
   if(socketHandle == INVALID_HANDLE)
      return;
   
   MqlTick tick;
   if(!SymbolInfoTick(currentSymbol, tick))
      return;
   
   // Get symbol info
   double point = SymbolInfoDouble(currentSymbol, SYMBOL_POINT);
   int digits = (int)SymbolInfoInteger(currentSymbol, SYMBOL_DIGITS);
   double contractSize = SymbolInfoDouble(currentSymbol, SYMBOL_TRADE_CONTRACT_SIZE);
   double minLot = SymbolInfoDouble(currentSymbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(currentSymbol, SYMBOL_VOLUME_MAX);
   double lotStep = SymbolInfoDouble(currentSymbol, SYMBOL_VOLUME_STEP);
   
   // Get account info
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double margin = AccountInfoDouble(ACCOUNT_MARGIN);
   double freeMargin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   double profit = AccountInfoDouble(ACCOUNT_PROFIT);
   int leverage = (int)AccountInfoInteger(ACCOUNT_LEVERAGE);
   
   // Build JSON message
   string message = StringFormat(
      "{\"type\":\"market_data\","
      "\"symbol\":\"%s\","
      "\"bid\":%.5f,"
      "\"ask\":%.5f,"
      "\"spread\":%d,"
      "\"time\":\"%s\","
      "\"point\":%.5f,"
      "\"digits\":%d,"
      "\"contract_size\":%.2f,"
      "\"min_lot\":%.2f,"
      "\"max_lot\":%.2f,"
      "\"lot_step\":%.2f,"
      "\"balance\":%.2f,"
      "\"equity\":%.2f,"
      "\"margin\":%.2f,"
      "\"free_margin\":%.2f,"
      "\"profit\":%.2f,"
      "\"leverage\":%d,"
      "\"open_positions\":%d}\n",
      currentSymbol,
      tick.bid,
      tick.ask,
      (int)((tick.ask - tick.bid) / point),
      TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS),
      point,
      digits,
      contractSize,
      minLot,
      maxLot,
      lotStep,
      balance,
      equity,
      margin,
      freeMargin,
      profit,
      leverage,
      CountOpenPositions()
   );
   
   SendToPython(message);
}

//+------------------------------------------------------------------+
//| Send open positions to Python                                    |
//+------------------------------------------------------------------+
void SendPositionsData()
{
   if(socketHandle == INVALID_HANDLE)
      return;
   
   int total = PositionsTotal();
   
   for(int i = 0; i < total; i++)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket <= 0)
         continue;
      
      if(PositionGetString(POSITION_SYMBOL) != currentSymbol)
         continue;
      
      if(PositionGetInteger(POSITION_MAGIC) != MagicNumber)
         continue;
      
      string posType = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? "BUY" : "SELL";
      
      string message = StringFormat(
         "{\"type\":\"position\","
         "\"ticket\":%I64u,"
         "\"symbol\":\"%s\","
         "\"pos_type\":\"%s\","
         "\"volume\":%.2f,"
         "\"price_open\":%.5f,"
         "\"price_current\":%.5f,"
         "\"sl\":%.5f,"
         "\"tp\":%.5f,"
         "\"profit\":%.2f,"
         "\"comment\":\"%s\"}\n",
         ticket,
         PositionGetString(POSITION_SYMBOL),
         posType,
         PositionGetDouble(POSITION_VOLUME),
         PositionGetDouble(POSITION_PRICE_OPEN),
         PositionGetDouble(POSITION_PRICE_CURRENT),
         PositionGetDouble(POSITION_SL),
         PositionGetDouble(POSITION_TP),
         PositionGetDouble(POSITION_PROFIT),
         PositionGetString(POSITION_COMMENT)
      );
      
      SendToPython(message);
   }
}

//+------------------------------------------------------------------+
//| Check for commands from Python                                   |
//+------------------------------------------------------------------+
void CheckPythonCommands()
{
   if(socketHandle == INVALID_HANDLE)
      return;
   
   string received = "";
   uint len;
   uchar buffer[];
   
   do
   {
      len = SocketIsReadable(socketHandle);
      if(len > 0)
      {
         ArrayResize(buffer, len);
         int bytes = SocketRead(socketHandle, buffer, len, 100);
         if(bytes > 0)
            received += CharArrayToString(buffer, 0, bytes);
      }
   }
   while(len > 0);
   
   if(received != "")
   {
      ProcessCommand(received);
   }
}

//+------------------------------------------------------------------+
//| Process command from Python                                      |
//+------------------------------------------------------------------+
void ProcessCommand(string command)
{
   Print("Received command: ", command);
   
   // Parse JSON command (simple parsing)
   if(StringFind(command, "\"action\":\"BUY\"") >= 0)
   {
      ExecuteBuyOrder(command);
   }
   else if(StringFind(command, "\"action\":\"SELL\"") >= 0)
   {
      ExecuteSellOrder(command);
   }
   else if(StringFind(command, "\"action\":\"CLOSE\"") >= 0)
   {
      ClosePosition(command);
   }
   else if(StringFind(command, "\"action\":\"MODIFY\"") >= 0)
   {
      ModifyPosition(command);
   }
   else if(StringFind(command, "\"action\":\"GET_POSITIONS\"") >= 0)
   {
      SendPositionsData();
   }
   else if(StringFind(command, "\"action\":\"GET_RATES\"") >= 0)
   {
      SendHistoricalRates(command);
   }
}

//+------------------------------------------------------------------+
//| Execute BUY order                                                |
//+------------------------------------------------------------------+
void ExecuteBuyOrder(string command)
{
   if(!EnableAutoTrading)
   {
      SendResponse("ERROR", "Auto trading disabled");
      return;
   }
   
   // Parse command (simple extraction)
   double volume = ExtractDouble(command, "volume");
   double sl = ExtractDouble(command, "sl");
   double tp = ExtractDouble(command, "tp");
   string comment = ExtractString(command, "comment");
   
   if(volume <= 0)
      volume = SymbolInfoDouble(currentSymbol, SYMBOL_VOLUME_MIN);
   
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = currentSymbol;
   request.volume = volume;
   request.type = ORDER_TYPE_BUY;
   request.price = SymbolInfoDouble(currentSymbol, SYMBOL_ASK);
   request.sl = sl;
   request.tp = tp;
   request.deviation = 20;
   request.magic = MagicNumber;
   request.comment = comment;
   request.type_filling = ORDER_FILLING_IOC;
   
   if(OrderSend(request, result))
   {
      if(result.retcode == TRADE_RETCODE_DONE)
      {
         string response = StringFormat(
            "{\"type\":\"order_result\","
            "\"success\":true,"
            "\"action\":\"BUY\","
            "\"ticket\":%I64u,"
            "\"volume\":%.2f,"
            "\"price\":%.5f,"
            "\"sl\":%.5f,"
            "\"tp\":%.5f}\n",
            result.order,
            result.volume,
            result.price,
            sl,
            tp
         );
         SendToPython(response);
      }
      else
      {
         SendResponse("ERROR", StringFormat("Order failed: %d", result.retcode));
      }
   }
   else
   {
      SendResponse("ERROR", "Order send failed");
   }
}

//+------------------------------------------------------------------+
//| Execute SELL order                                               |
//+------------------------------------------------------------------+
void ExecuteSellOrder(string command)
{
   if(!EnableAutoTrading)
   {
      SendResponse("ERROR", "Auto trading disabled");
      return;
   }
   
   double volume = ExtractDouble(command, "volume");
   double sl = ExtractDouble(command, "sl");
   double tp = ExtractDouble(command, "tp");
   string comment = ExtractString(command, "comment");
   
   if(volume <= 0)
      volume = SymbolInfoDouble(currentSymbol, SYMBOL_VOLUME_MIN);
   
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.symbol = currentSymbol;
   request.volume = volume;
   request.type = ORDER_TYPE_SELL;
   request.price = SymbolInfoDouble(currentSymbol, SYMBOL_BID);
   request.sl = sl;
   request.tp = tp;
   request.deviation = 20;
   request.magic = MagicNumber;
   request.comment = comment;
   request.type_filling = ORDER_FILLING_IOC;
   
   if(OrderSend(request, result))
   {
      if(result.retcode == TRADE_RETCODE_DONE)
      {
         string response = StringFormat(
            "{\"type\":\"order_result\","
            "\"success\":true,"
            "\"action\":\"SELL\","
            "\"ticket\":%I64u,"
            "\"volume\":%.2f,"
            "\"price\":%.5f,"
            "\"sl\":%.5f,"
            "\"tp\":%.5f}\n",
            result.order,
            result.volume,
            result.price,
            sl,
            tp
         );
         SendToPython(response);
      }
      else
      {
         SendResponse("ERROR", StringFormat("Order failed: %d", result.retcode));
      }
   }
   else
   {
      SendResponse("ERROR", "Order send failed");
   }
}

//+------------------------------------------------------------------+
//| Close position                                                    |
//+------------------------------------------------------------------+
void ClosePosition(string command)
{
   ulong ticket = (ulong)ExtractDouble(command, "ticket");
   
   if(!PositionSelectByTicket(ticket))
   {
      SendResponse("ERROR", "Position not found");
      return;
   }
   
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_DEAL;
   request.position = ticket;
   request.symbol = PositionGetString(POSITION_SYMBOL);
   request.volume = PositionGetDouble(POSITION_VOLUME);
   request.deviation = 20;
   request.magic = MagicNumber;
   request.comment = "Closed by Python";
   request.type_filling = ORDER_FILLING_IOC;
   
   if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
   {
      request.type = ORDER_TYPE_SELL;
      request.price = SymbolInfoDouble(request.symbol, SYMBOL_BID);
   }
   else
   {
      request.type = ORDER_TYPE_BUY;
      request.price = SymbolInfoDouble(request.symbol, SYMBOL_ASK);
   }
   
   if(OrderSend(request, result))
   {
      if(result.retcode == TRADE_RETCODE_DONE)
      {
         SendResponse("SUCCESS", StringFormat("Position %I64u closed", ticket));
      }
      else
      {
         SendResponse("ERROR", StringFormat("Close failed: %d", result.retcode));
      }
   }
}

//+------------------------------------------------------------------+
//| Modify position                                                   |
//+------------------------------------------------------------------+
void ModifyPosition(string command)
{
   ulong ticket = (ulong)ExtractDouble(command, "ticket");
   double sl = ExtractDouble(command, "sl");
   double tp = ExtractDouble(command, "tp");
   
   if(!PositionSelectByTicket(ticket))
   {
      SendResponse("ERROR", "Position not found");
      return;
   }
   
   MqlTradeRequest request = {};
   MqlTradeResult result = {};
   
   request.action = TRADE_ACTION_SLTP;
   request.position = ticket;
   request.symbol = PositionGetString(POSITION_SYMBOL);
   request.sl = (sl > 0) ? sl : PositionGetDouble(POSITION_SL);
   request.tp = (tp > 0) ? tp : PositionGetDouble(POSITION_TP);
   
   if(OrderSend(request, result))
   {
      if(result.retcode == TRADE_RETCODE_DONE)
      {
         SendResponse("SUCCESS", StringFormat("Position %I64u modified", ticket));
      }
      else
      {
         SendResponse("ERROR", StringFormat("Modify failed: %d", result.retcode));
      }
   }
}

//+------------------------------------------------------------------+
//| Send historical rates                                             |
//+------------------------------------------------------------------+
void SendHistoricalRates(string command)
{
   int count = (int)ExtractDouble(command, "count");
   int timeframe = (int)ExtractDouble(command, "timeframe");
   
   if(count <= 0) count = 100;
   if(timeframe <= 0) timeframe = PERIOD_M15;
   
   MqlRates rates[];
   int copied = CopyRates(currentSymbol, (ENUM_TIMEFRAMES)timeframe, 0, count, rates);
   
   if(copied > 0)
   {
      string response = "{\"type\":\"rates\",\"data\":[";
      
      for(int i = 0; i < copied; i++)
      {
         if(i > 0) response += ",";
         response += StringFormat(
            "{\"time\":\"%s\",\"open\":%.5f,\"high\":%.5f,\"low\":%.5f,\"close\":%.5f,\"volume\":%I64d}",
            TimeToString(rates[i].time, TIME_DATE|TIME_SECONDS),
            rates[i].open,
            rates[i].high,
            rates[i].low,
            rates[i].close,
            rates[i].tick_volume
         );
      }
      
      response += "]}\n";
      SendToPython(response);
   }
   else
   {
      SendResponse("ERROR", "Failed to get rates");
   }
}

//+------------------------------------------------------------------+
//| Send heartbeat                                                    |
//+------------------------------------------------------------------+
void SendHeartbeat()
{
   string message = StringFormat(
      "{\"type\":\"heartbeat\",\"time\":\"%s\",\"status\":\"alive\"}\n",
      TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS)
   );
   SendToPython(message);
}

//+------------------------------------------------------------------+
//| Send response to Python                                          |
//+------------------------------------------------------------------+
void SendResponse(string status, string message)
{
   string response = StringFormat(
      "{\"type\":\"response\",\"status\":\"%s\",\"message\":\"%s\"}\n",
      status,
      message
   );
   SendToPython(response);
}

//+------------------------------------------------------------------+
//| Send message to Python                                           |
//+------------------------------------------------------------------+
void SendToPython(string message)
{
   if(socketHandle == INVALID_HANDLE)
      return;
   
   uchar data[];
   int len = StringToCharArray(message, data, 0, WHOLE_ARRAY, CP_UTF8) - 1;
   if(len > 0)
      SocketSend(socketHandle, data, len);
}

//+------------------------------------------------------------------+
//| Extract double value from JSON                                   |
//+------------------------------------------------------------------+
double ExtractDouble(string json, string key)
{
   int pos = StringFind(json, "\"" + key + "\":");
   if(pos < 0) return 0;
   
   pos += StringLen(key) + 3;
   int endPos = StringFind(json, ",", pos);
   if(endPos < 0) endPos = StringFind(json, "}", pos);
   
   string value = StringSubstr(json, pos, endPos - pos);
   return StringToDouble(value);
}

//+------------------------------------------------------------------+
//| Extract string value from JSON                                   |
//+------------------------------------------------------------------+
string ExtractString(string json, string key)
{
   int pos = StringFind(json, "\"" + key + "\":\"");
   if(pos < 0) return "";
   
   pos += StringLen(key) + 4;
   int endPos = StringFind(json, "\"", pos);
   
   return StringSubstr(json, pos, endPos - pos);
}

//+------------------------------------------------------------------+
//| Count open positions                                             |
//+------------------------------------------------------------------+
int CountOpenPositions()
{
   int count = 0;
   int total = PositionsTotal();
   
   for(int i = 0; i < total; i++)
   {
      if(PositionGetTicket(i) > 0)
      {
         if(PositionGetString(POSITION_SYMBOL) == currentSymbol &&
            PositionGetInteger(POSITION_MAGIC) == MagicNumber)
         {
            count++;
         }
      }
   }
   
   return count;
}
//+------------------------------------------------------------------+
