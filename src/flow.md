# **Algo-s: Flow**

## **Goals**

- **Only profitable trades**
- **Max time in trade: Until end of week**
- **Max profit: 2%**
- **Max loss: 1%**
- **Max active trades: 3**
- **Refresh rate: 15 min**

## **Flow**

> **This flow gets run every 15 minutes or what the current refresh rate is during active trading hours (USA)**

### **1. Macro view**

- **General trends**
  - S&P, DOW, Texas stock exchange, Nasdaq, ftse
    - Week trends
    - Day trends
    - Month trends
    - 6 month trends
  - News
    - Today
    - Developing stories
    - Headlines

### **2. Stock selection**

- **Select stocks based on news**
- **Select stocks based on most consistent risers -> As many days ended in green as possible of the last 2 weeks**
- **Max stocks: 50**

### **3. Trading decision**

```mermaid
**flowchart TD
    START1(("Consistent-based"))
    START2(("News-based"))

    A["Get relevant news (if any)"]
    B["Find industry news"]
    C["Find financials"]
    D{"Financials, industry, company & macro news for a trading decision"}

    START1 --> A --> B
    START2 --> B --> C --> D

    D --> END1(("Don't trade"))
    D --> E{"Was a neural network recently trained on recent ticker data?"}
    E -->|yes| END2(("NN-based trading decision"))
    E -->|No| G["Train, fine-tune & test with LLM supervisor"] --> E**

```
