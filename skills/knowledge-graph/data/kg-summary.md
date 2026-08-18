#KGML v2 | 9e 8r | depth:2 | 2026-08-18

[governance]
SOP-RECURSIVE.md (recursive learning + model hygiene)(DED):decision — date:2026-08-18, status:active

[infra]
DeepSeek (provider)(PR):platform — baseUrl:https://api.deepseek.com, flagship:deepseek-v4-pro, pricing:direct-pay
Kimi / Moonshot (provider)(PR2):platform — flagship:kimi-k3
Qwen / DashScope (provider)(PRP):platform — flagship:qwen3.8-max, pricing:direct-pay

[person]
Olivier 'Olive' Castagne(HU):human — email:ol.castagne@gmail.com, tz:Europe/Madrid

[trading]
Hyperliquid trading ops desk(DE):project — script:skills/hyperliquid-ops, doctrine:SKILL.md 79 rules
  Hyperliquid desk architecture v2.6.4(DE2):project — frozen_until:50 graded calls, sizing:flat 0.33R, stop:80% of liquidation, breaker:3 stops / 5 days
    Bounded independence in audit layer(FIF):knowledge — severity:critical
    R is fictional on xyz synthetics off-hours(FI):knowledge — severity:critical

%rel-summary
uses(3) has(3) used_with(1) owns(1)
%key-relations
  [Hyperliquid trading ops desk]
    Hyperliquid trading ops desk >uses> DeepSeek (provider)
    Hyperliquid trading ops desk >uses> Qwen / DashScope (provider)
    Hyperliquid trading ops desk >uses> Kimi / Moonshot (provider)
    Hyperliquid trading ops desk >has> SOP-RECURSIVE.md (recursive learning + model hygiene)
    ... +2 more
  [DeepSeek (provider)]
    DeepSeek (provider) >used_with> Qwen / DashScope (provider)
  [Olivier 'Olive' Castagne]
    Olivier 'Olive' Castagne >owns> Hyperliquid trading ops desk

%types platform:3 project:2 knowledge:2 decision:1 human:1
