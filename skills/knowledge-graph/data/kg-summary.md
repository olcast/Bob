#KGML v2 | 5e 5r | depth:0 | 2026-08-18

[governance]
SOP-RECURSIVE.md (recursive learning + model hygiene)(DED):decision — date:2026-08-18, status:active

[infra]
DeepSeek (provider)(PR):platform — baseUrl:https://api.deepseek.com, flagship:deepseek-v4-pro, pricing:direct-pay
Kimi / Moonshot (provider)(PR2):platform — flagship:kimi-k3
Qwen / DashScope (provider)(PRP):platform — flagship:qwen3.8-max, pricing:direct-pay

[trading]
Hyperliquid trading ops desk(DE):project — script:skills/hyperliquid-ops, doctrine:SKILL.md 79 rules

%rel-summary
uses(3) has(1) used_with(1)
%key-relations
  [Hyperliquid trading ops desk]
    Hyperliquid trading ops desk >uses> DeepSeek (provider)
    Hyperliquid trading ops desk >uses> Qwen / DashScope (provider)
    Hyperliquid trading ops desk >uses> Kimi / Moonshot (provider)
    Hyperliquid trading ops desk >has> SOP-RECURSIVE.md (recursive learning + model hygiene)
  [DeepSeek (provider)]
    DeepSeek (provider) >used_with> Qwen / DashScope (provider)

%types platform:3 project:1 decision:1
