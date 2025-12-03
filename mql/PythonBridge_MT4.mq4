//+------------------------------------------------------------------+
//|                                         PythonBridge_MT4.mq4     |
//|                                   Python Trading Bot Bridge      |
//|                                   MetaTrader 4 Expert Advisor    |
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
input int      Slippage = 20;                 // Slippage in points

//--- Global variables
int socketHandle = INVALID_HANDLE;
datetime lastHeartbeat;
string currentSymbol;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   Print("=== Python Bridge MT4 EA Starting ===");
   
   // Set symbol
   if(TradingSymbol == "")
      currentSymbol = Symbol();
   else
      currentSymbol = TradingSymbol;
   
   Print("Symbol: ", currentSymbol);
   Print("Python Server: ", PythonHost, ":", PythonPort);
   Print("Magic Number: ", MagicNumber);
   
   // Note: MT4 doesn't support socket connections like MT5
   // You need to use file-based communication or DLL
   Print("⚠️ MT4 Note: Socket communication requires external DLL");
   Print("   Alternative: Using file-based communication in Experts/Files/");
   
   lastHeartbeat = TimeCurrent();
   
   // Create communication files
   InitFileComm();
   
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   Print("=== Python Bridge MT4 EA Stopping ===");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   // Send market data
   SendMarketDataToFile();
   
   // Check for Python commands
   CheckPythonCommandsFromFile();
   
   // Heartbeat
   if(TimeCurrent() - lastHeartbeat >= HeartbeatSeconds)
   {
      SendHeartbeatToFile();
      lastHeartbeat = TimeCurrent();
   }
}

//+------------------------------------------------------------------+
//| Initialize file communication                                    |
//+------------------------------------------------------------------+
void InitFileComm()
{
   // Create empty command file
   int handle = FileOpen("python_commands.json", FILE_WRITE|FILE_TXT);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, "");
      FileClose(handle);
   }
   
   Print("✅ File communication initialized");
   Print("   Commands: Experts/Files/python_commands.json");
   Print("   Market Data: Experts/Files/mt4_market_data.json");
}

//+------------------------------------------------------------------+
//| Send market data to file                                         |
//+------------------------------------------------------------------+
void SendMarketDataToFile()
{
   // Get symbol info
   double bid = MarketInfo(currentSymbol, MODE_BID);
   double ask = MarketInfo(currentSymbol, MODE_ASK);
   double point = MarketInfo(currentSymbol, MODE_POINT);
   int digits = (int)MarketInfo(currentSymbol, MODE_DIGITS);
   double minLot = MarketInfo(currentSymbol, MODE_MINLOT);
   double maxLot = MarketInfo(currentSymbol, MODE_MAXLOT);
   double lotStep = MarketInfo(currentSymbol, MODE_LOTSTEP);
   double contractSize = MarketInfo(currentSymbol, MODE_LOTSIZE);
   int spread = (int)MarketInfo(currentSymbol, MODE_SPREAD);
   
   // Get account info
   double balance = AccountBalance();
   double equity = AccountEquity();
   double margin = AccountMargin();
   double freeMargin = AccountFreeMargin();
   double profit = AccountProfit();
   int leverage = AccountLeverage();
   
   // Build JSON message
   string message = StringConcatenate(
      "{",
      "\"type\":\"market_data\",",
      "\"symbol\":\"", currentSymbol, "\",",
      "\"bid\":", DoubleToStr(bid, digits), ",",
      "\"ask\":", DoubleToStr(ask, digits), ",",
      "\"spread\":", IntegerToString(spread), ",",
      "\"time\":\"", TimeToStr(TimeCurrent(), TIME_DATE|TIME_SECONDS), "\",",
      "\"point\":", DoubleToStr(point, digits+1), ",",
      "\"digits\":", IntegerToString(digits), ",",
      "\"contract_size\":", DoubleToStr(contractSize, 2), ",",
      "\"min_lot\":", DoubleToStr(minLot, 2), ",",
      "\"max_lot\":", DoubleToStr(maxLot, 2), ",",
      "\"lot_step\":", DoubleToStr(lotStep, 2), ",",
      "\"balance\":", DoubleToStr(balance, 2), ",",
      "\"equity\":", DoubleToStr(equity, 2), ",",
      "\"margin\":", DoubleToStr(margin, 2), ",",
      "\"free_margin\":", DoubleToStr(freeMargin, 2), ",",
      "\"profit\":", DoubleToStr(profit, 2), ",",
      "\"leverage\":", IntegerToString(leverage), ",",
      "\"open_positions\":", IntegerToString(CountOpenPositions()),
      "}"
   );
   
   // Write to file
   int handle = FileOpen("mt4_market_data.json", FILE_WRITE|FILE_TXT);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, message);
      FileClose(handle);
   }
}

//+------------------------------------------------------------------+
//| Send open positions to file                                      |
//+------------------------------------------------------------------+
void SendPositionsDataToFile()
{
   int total = OrdersTotal();
   string positions = "[";
   bool first = true;
   
   for(int i = 0; i < total; i++)
   {
      if(!OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
         continue;
      
      if(OrderSymbol() != currentSymbol)
         continue;
      
      if(OrderMagicNumber() != MagicNumber)
         continue;
      
      if(OrderType() > OP_SELL)
         continue; // Skip pending orders
      
      string posType = (OrderType() == OP_BUY) ? "BUY" : "SELL";
      
      if(!first) positions = StringConcatenate(positions, ",");
      first = false;
      
      positions = StringConcatenate(
         positions,
         "{",
         "\"ticket\":", IntegerToString(OrderTicket()), ",",
         "\"symbol\":\"", OrderSymbol(), "\",",
         "\"pos_type\":\"", posType, "\",",
         "\"volume\":", DoubleToStr(OrderLots(), 2), ",",
         "\"price_open\":", DoubleToStr(OrderOpenPrice(), Digits), ",",
         "\"price_current\":", DoubleToStr(OrderClosePrice(), Digits), ",",
         "\"sl\":", DoubleToStr(OrderStopLoss(), Digits), ",",
         "\"tp\":", DoubleToStr(OrderTakeProfit(), Digits), ",",
         "\"profit\":", DoubleToStr(OrderProfit(), 2), ",",
         "\"comment\":\"", OrderComment(), "\"",
         "}"
      );
   }
   
   positions = StringConcatenate(positions, "]");
   
   // Write to file
   int handle = FileOpen("mt4_positions.json", FILE_WRITE|FILE_TXT);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, positions);
      FileClose(handle);
   }
}

//+------------------------------------------------------------------+
//| Check for commands from Python                                   |
//+------------------------------------------------------------------+
void CheckPythonCommandsFromFile()
{
   int handle = FileOpen("python_commands.json", FILE_READ|FILE_TXT);
   if(handle == INVALID_HANDLE)
      return;
   
   string command = "";
   while(!FileIsEnding(handle))
   {
      command = StringConcatenate(command, FileReadString(handle));
   }
   FileClose(handle);
   
   if(StringLen(command) > 10)
   {
      ProcessCommand(command);
      
      // Clear command file after processing
      handle = FileOpen("python_commands.json", FILE_WRITE|FILE_TXT);
      if(handle != INVALID_HANDLE)
      {
         FileWrite(handle, "");
         FileClose(handle);
      }
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
      SendPositionsDataToFile();
   }
   else if(StringFind(command, "\"action\":\"GET_RATES\"") >= 0)
   {
      SendHistoricalRatesToFile(command);
   }
}

//+------------------------------------------------------------------+
//| Execute BUY order                                                |
//+------------------------------------------------------------------+
void ExecuteBuyOrder(string command)
{
   if(!EnableAutoTrading)
   {
      SendResponseToFile("ERROR", "Auto trading disabled");
      return;
   }
   
   // Parse command
   double volume = ExtractDouble(command, "volume");
   double sl = ExtractDouble(command, "sl");
   double tp = ExtractDouble(command, "tp");
   string comment = ExtractString(command, "comment");
   
   if(volume <= 0)
      volume = MarketInfo(currentSymbol, MODE_MINLOT);
   
   double price = MarketInfo(currentSymbol, MODE_ASK);
   
   int ticket = OrderSend(
      currentSymbol,
      OP_BUY,
      volume,
      price,
      Slippage,
      sl,
      tp,
      comment,
      MagicNumber,
      0,
      clrGreen
   );
   
   if(ticket > 0)
   {
      string response = StringConcatenate(
         "{",
         "\"type\":\"order_result\",",
         "\"success\":true,",
         "\"action\":\"BUY\",",
         "\"ticket\":", IntegerToString(ticket), ",",
         "\"volume\":", DoubleToStr(volume, 2), ",",
         "\"price\":", DoubleToStr(price, Digits), ",",
         "\"sl\":", DoubleToStr(sl, Digits), ",",
         "\"tp\":", DoubleToStr(tp, Digits),
         "}"
      );
      SendResponseToFile("SUCCESS", response);
   }
   else
   {
      SendResponseToFile("ERROR", StringConcatenate("Order failed: ", IntegerToString(GetLastError())));
   }
}

//+------------------------------------------------------------------+
//| Execute SELL order                                               |
//+------------------------------------------------------------------+
void ExecuteSellOrder(string command)
{
   if(!EnableAutoTrading)
   {
      SendResponseToFile("ERROR", "Auto trading disabled");
      return;
   }
   
   double volume = ExtractDouble(command, "volume");
   double sl = ExtractDouble(command, "sl");
   double tp = ExtractDouble(command, "tp");
   string comment = ExtractString(command, "comment");
   
   if(volume <= 0)
      volume = MarketInfo(currentSymbol, MODE_MINLOT);
   
   double price = MarketInfo(currentSymbol, MODE_BID);
   
   int ticket = OrderSend(
      currentSymbol,
      OP_SELL,
      volume,
      price,
      Slippage,
      sl,
      tp,
      comment,
      MagicNumber,
      0,
      clrRed
   );
   
   if(ticket > 0)
   {
      string response = StringConcatenate(
         "{",
         "\"type\":\"order_result\",",
         "\"success\":true,",
         "\"action\":\"SELL\",",
         "\"ticket\":", IntegerToString(ticket), ",",
         "\"volume\":", DoubleToStr(volume, 2), ",",
         "\"price\":", DoubleToStr(price, Digits), ",",
         "\"sl\":", DoubleToStr(sl, Digits), ",",
         "\"tp\":", DoubleToStr(tp, Digits),
         "}"
      );
      SendResponseToFile("SUCCESS", response);
   }
   else
   {
      SendResponseToFile("ERROR", StringConcatenate("Order failed: ", IntegerToString(GetLastError())));
   }
}

//+------------------------------------------------------------------+
//| Close position                                                    |
//+------------------------------------------------------------------+
void ClosePosition(string command)
{
   int ticket = (int)ExtractDouble(command, "ticket");
   
   if(!OrderSelect(ticket, SELECT_BY_TICKET))
   {
      SendResponseToFile("ERROR", "Order not found");
      return;
   }
   
   bool result = false;
   
   if(OrderType() == OP_BUY)
   {
      result = OrderClose(ticket, OrderLots(), MarketInfo(OrderSymbol(), MODE_BID), Slippage, clrRed);
   }
   else if(OrderType() == OP_SELL)
   {
      result = OrderClose(ticket, OrderLots(), MarketInfo(OrderSymbol(), MODE_ASK), Slippage, clrGreen);
   }
   
   if(result)
   {
      SendResponseToFile("SUCCESS", StringConcatenate("Position ", IntegerToString(ticket), " closed"));
   }
   else
   {
      SendResponseToFile("ERROR", StringConcatenate("Close failed: ", IntegerToString(GetLastError())));
   }
}

//+------------------------------------------------------------------+
//| Modify position                                                   |
//+------------------------------------------------------------------+
void ModifyPosition(string command)
{
   int ticket = (int)ExtractDouble(command, "ticket");
   double sl = ExtractDouble(command, "sl");
   double tp = ExtractDouble(command, "tp");
   
   if(!OrderSelect(ticket, SELECT_BY_TICKET))
   {
      SendResponseToFile("ERROR", "Order not found");
      return;
   }
   
   if(sl <= 0) sl = OrderStopLoss();
   if(tp <= 0) tp = OrderTakeProfit();
   
   bool result = OrderModify(ticket, OrderOpenPrice(), sl, tp, 0, clrBlue);
   
   if(result)
   {
      SendResponseToFile("SUCCESS", StringConcatenate("Position ", IntegerToString(ticket), " modified"));
   }
   else
   {
      SendResponseToFile("ERROR", StringConcatenate("Modify failed: ", IntegerToString(GetLastError())));
   }
}

//+------------------------------------------------------------------+
//| Send historical rates to file                                    |
//+------------------------------------------------------------------+
void SendHistoricalRatesToFile(string command)
{
   int count = (int)ExtractDouble(command, "count");
   int timeframe = (int)ExtractDouble(command, "timeframe");
   
   if(count <= 0) count = 100;
   if(timeframe <= 0) timeframe = PERIOD_M15;
   
   string rates = "[";
   
   for(int i = count - 1; i >= 0; i--)
   {
      if(i < count - 1) rates = StringConcatenate(rates, ",");
      
      datetime time = iTime(currentSymbol, timeframe, i);
      double open = iOpen(currentSymbol, timeframe, i);
      double high = iHigh(currentSymbol, timeframe, i);
      double low = iLow(currentSymbol, timeframe, i);
      double close = iClose(currentSymbol, timeframe, i);
      long volume = iVolume(currentSymbol, timeframe, i);
      
      rates = StringConcatenate(
         rates,
         "{",
         "\"time\":\"", TimeToStr(time, TIME_DATE|TIME_SECONDS), "\",",
         "\"open\":", DoubleToStr(open, Digits), ",",
         "\"high\":", DoubleToStr(high, Digits), ",",
         "\"low\":", DoubleToStr(low, Digits), ",",
         "\"close\":", DoubleToStr(close, Digits), ",",
         "\"volume\":", IntegerToString(volume),
         "}"
      );
   }
   
   rates = StringConcatenate(rates, "]");
   
   // Write to file
   int handle = FileOpen("mt4_rates.json", FILE_WRITE|FILE_TXT);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, "{\"type\":\"rates\",\"data\":", rates, "}");
      FileClose(handle);
   }
}

//+------------------------------------------------------------------+
//| Send heartbeat to file                                           |
//+------------------------------------------------------------------+
void SendHeartbeatToFile()
{
   string message = StringConcatenate(
      "{",
      "\"type\":\"heartbeat\",",
      "\"time\":\"", TimeToStr(TimeCurrent(), TIME_DATE|TIME_SECONDS), "\",",
      "\"status\":\"alive\"",
      "}"
   );
   
   int handle = FileOpen("mt4_heartbeat.json", FILE_WRITE|FILE_TXT);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, message);
      FileClose(handle);
   }
}

//+------------------------------------------------------------------+
//| Send response to file                                            |
//+------------------------------------------------------------------+
void SendResponseToFile(string status, string message)
{
   string response = StringConcatenate(
      "{",
      "\"type\":\"response\",",
      "\"status\":\"", status, "\",",
      "\"message\":\"", message, "\"",
      "}"
   );
   
   int handle = FileOpen("mt4_response.json", FILE_WRITE|FILE_TXT);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, response);
      FileClose(handle);
   }
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
   return StrToDouble(value);
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
   int total = OrdersTotal();
   
   for(int i = 0; i < total; i++)
   {
      if(OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if(OrderSymbol() == currentSymbol && 
            OrderMagicNumber() == MagicNumber &&
            OrderType() <= OP_SELL)
         {
            count++;
         }
      }
   }
   
   return count;
}
//+------------------------------------------------------------------+
