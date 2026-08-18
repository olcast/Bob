#KGML v2 | 16e 18r | depth:2 | 2026-08-18

[🔨 Projects]
VCP — Verified Cognitive Protocol(VC):project — standard_version:V1.2, author:Olivier Castagne, license:open + vendor-neutral, sector:AI accountability / trust infrastructure, date:2026-08-18
  immutability ≠ correctness (VCP gap)(VCV):concept — severity:critical
    citigroup_2022(CI):event — date:2022, detail:$444B fat-finger, $189B reached market
    flash_crash_2010(FL):event — date:2010, detail:~$1T value evaporated, 5mo investigation
    knight_capital_2012(KN):event — date:2012, loss:$440M in 45min, cause:failed software update
  receipt→ledger→notary chain(VC3):concept
  zero-knowledge proof (prove rules, hide weights)(VC2):concept

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
has(5) related_to(4) uses(3) part_of(2) used_with(1) owns(1) created(1) depends_on(1)
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
    Olivier 'Olive' Castagne >created> VCP — Verified Cognitive Protocol
  [VCP — Verified Cognitive Protocol]
    VCP — Verified Cognitive Protocol >related_to> SOP-RECURSIVE.md (recursive learning + model hygiene)
    immutability ≠ correctness (VCP gap) >related_to> knight_capital_2012
    immutability ≠ correctness (VCP gap) >related_to> flash_crash_2010
    immutability ≠ correctness (VCP gap) >related_to> citigroup_2022
    ... +5 more

%types platform:3 project:3 concept:3 event:3 knowledge:2 decision:1 human:1
