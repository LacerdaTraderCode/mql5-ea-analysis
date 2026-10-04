//+------------------------------------------------------------------+
//|                                    MovingAverageCrossoverEA.mq5   |
//|       Moving average crossover EA with a CSV trade log export    |
//|                        https://github.com/LacerdaTraderCode      |
//+------------------------------------------------------------------+
#property copyright "Wagner Lacerda"
#property link      "https://github.com/LacerdaTraderCode"
#property version   "1.00"

#include <Trade/Trade.mqh>

input int                 FastPeriod       = 10;
input int                 SlowPeriod       = 30;
input ENUM_MA_METHOD      MaMethod         = MODE_EMA;
input ENUM_APPLIED_PRICE  AppliedPrice     = PRICE_CLOSE;
input double               RiskPercent      = 1.0;    // Percent of balance risked per trade
input double               StopLossPoints   = 500;
input double               TakeProfitPoints = 1000;
input string               TradeLogFileName = "ma_crossover_trades.csv";

CTrade trade;
int    fastMaHandle;
int    slowMaHandle;
double fastMaBuffer[];
double slowMaBuffer[];
int    tradeLogHandle = INVALID_HANDLE;

//+------------------------------------------------------------------+
int OnInit()
{
   fastMaHandle = iMA(_Symbol, _Period, FastPeriod, 0, MaMethod, AppliedPrice);
   slowMaHandle = iMA(_Symbol, _Period, SlowPeriod, 0, MaMethod, AppliedPrice);

   if(fastMaHandle == INVALID_HANDLE || slowMaHandle == INVALID_HANDLE)
     {
      Print("Failed to create moving average handles");
      return INIT_FAILED;
     }

   ArraySetAsSeries(fastMaBuffer, true);
   ArraySetAsSeries(slowMaBuffer, true);

   // FILE_COMMON writes to the shared MQL5\Files\Common folder rather than
   // this terminal's own data folder, so the Python analysis side can read
   // the export without having to locate a specific terminal installation.
   bool fileExists = FileIsExist(TradeLogFileName, FILE_COMMON);
   tradeLogHandle = FileOpen(TradeLogFileName, FILE_READ | FILE_WRITE | FILE_CSV | FILE_COMMON);
   if(tradeLogHandle == INVALID_HANDLE)
     {
      Print("Failed to open trade log file: ", TradeLogFileName);
      return INIT_FAILED;
     }
   if(!fileExists)
     {
      FileWrite(tradeLogHandle, "close_time", "symbol", "direction", "exit_price", "lots", "profit", "balance_after");
     }
   FileSeek(tradeLogHandle, 0, SEEK_END);

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   IndicatorRelease(fastMaHandle);
   IndicatorRelease(slowMaHandle);
   if(tradeLogHandle != INVALID_HANDLE)
      FileClose(tradeLogHandle);
}

//+------------------------------------------------------------------+
bool HasOpenPosition()
{
   return PositionSelect(_Symbol);
}

//+------------------------------------------------------------------+
double CalculateLotSize(double stopLossPoints)
{
   double balance    = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = balance * (RiskPercent / 100.0);
   double tickValue  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double pointValue = (tickSize > 0) ? tickValue / tickSize * _Point : tickValue;
   double lossPerLot = stopLossPoints * pointValue;

   if(lossPerLot <= 0)
      return SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);

   double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double lots    = MathFloor((riskAmount / lossPerLot) / lotStep) * lotStep;

   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   return MathMax(minLot, MathMin(maxLot, lots));
}

//+------------------------------------------------------------------+
void OnTick()
{
   if(CopyBuffer(fastMaHandle, 0, 0, 3, fastMaBuffer) < 3)
      return;
   if(CopyBuffer(slowMaHandle, 0, 0, 3, slowMaBuffer) < 3)
      return;

   bool crossedUp   = fastMaBuffer[2] < slowMaBuffer[2] && fastMaBuffer[1] > slowMaBuffer[1];
   bool crossedDown = fastMaBuffer[2] > slowMaBuffer[2] && fastMaBuffer[1] < slowMaBuffer[1];

   if(HasOpenPosition())
     {
      ENUM_POSITION_TYPE positionType = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
      bool shouldClose = (positionType == POSITION_TYPE_BUY && crossedDown) ||
                          (positionType == POSITION_TYPE_SELL && crossedUp);
      if(shouldClose)
         trade.PositionClose(_Symbol);
      return;
     }

   double ask   = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid   = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double point = _Point;
   double lots  = CalculateLotSize(StopLossPoints);

   if(crossedUp)
     {
      double stopLoss   = ask - StopLossPoints * point;
      double takeProfit = ask + TakeProfitPoints * point;
      trade.Buy(lots, _Symbol, ask, stopLoss, takeProfit, "MA crossover buy");
     }
   else if(crossedDown)
     {
      double stopLoss   = bid + StopLossPoints * point;
      double takeProfit = bid - TakeProfitPoints * point;
      trade.Sell(lots, _Symbol, bid, stopLoss, takeProfit, "MA crossover sell");
     }
}

//+------------------------------------------------------------------+
//| Logs every deal that closes a position, however it closed —      |
//| manually on a crossover, or hitting the stop loss or take profit |
//+------------------------------------------------------------------+
void OnTradeTransaction(
   const MqlTradeTransaction& transaction,
   const MqlTradeRequest&     request,
   const MqlTradeResult&      result
)
{
   if(transaction.type != TRADE_TRANSACTION_DEAL_ADD)
      return;
   if(!HistoryDealSelect(transaction.deal))
      return;
   if(HistoryDealGetInteger(transaction.deal, DEAL_ENTRY) != DEAL_ENTRY_OUT)
      return;

   long   dealType     = HistoryDealGetInteger(transaction.deal, DEAL_TYPE);
   // A deal that closes a position has the opposite type of that position:
   // a DEAL_TYPE_SELL closes a buy, and a DEAL_TYPE_BUY closes a sell.
   string direction    = (dealType == DEAL_TYPE_SELL) ? "buy" : "sell";
   double exitPrice    = HistoryDealGetDouble(transaction.deal, DEAL_PRICE);
   double lots         = HistoryDealGetDouble(transaction.deal, DEAL_VOLUME);
   double profit       = HistoryDealGetDouble(transaction.deal, DEAL_PROFIT);
   datetime closeTime  = (datetime)HistoryDealGetInteger(transaction.deal, DEAL_TIME);
   double balanceAfter = AccountInfoDouble(ACCOUNT_BALANCE);

   if(tradeLogHandle == INVALID_HANDLE)
      return;

   FileWrite(
      tradeLogHandle,
      TimeToString(closeTime, TIME_DATE | TIME_SECONDS),
      _Symbol,
      direction,
      exitPrice,
      lots,
      profit,
      balanceAfter
   );
   FileFlush(tradeLogHandle);
}
