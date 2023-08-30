# Changelog

## [0.8.0](https://github.com/blockanalitica/chain-harvester/compare/v0.7.0...v0.8.0) (2023-08-30)


### Features

* add get_events_for_contracts_topics ([#25](https://github.com/blockanalitica/chain-harvester/issues/25)) ([82a6da5](https://github.com/blockanalitica/chain-harvester/commit/82a6da567cd2b3994818fb60c892c82dfc160313))

## [0.7.0](https://github.com/blockanalitica/chain-harvester/compare/v0.6.0...v0.7.0) (2023-08-30)


### Features

* add gnosis chain ([#23](https://github.com/blockanalitica/chain-harvester/issues/23)) ([4d8da38](https://github.com/blockanalitica/chain-harvester/commit/4d8da38ac91ad602f8b1d75d513f21c79c9be02b))

## [0.6.0](https://github.com/blockanalitica/chain-harvester/compare/v0.5.0...v0.6.0) (2023-08-29)


### Features

* add get_events_for_contracts + EIP-1967 ABIs check ([#20](https://github.com/blockanalitica/chain-harvester/issues/20)) ([d291e1f](https://github.com/blockanalitica/chain-harvester/commit/d291e1fc5eb9f0251df725c2fbe780ad4ace3979))
* add get_events_for_topics ([#22](https://github.com/blockanalitica/chain-harvester/issues/22)) ([cb7813e](https://github.com/blockanalitica/chain-harvester/commit/cb7813eaa00a9b8a41da2a76bd8f80a7728dc873))

## [0.5.0](https://github.com/blockanalitica/chain-harvester/compare/v0.4.2...v0.5.0) (2023-08-29)


### Features

* changed event log decoder output ([#18](https://github.com/blockanalitica/chain-harvester/issues/18)) ([684b463](https://github.com/blockanalitica/chain-harvester/commit/684b463e345f4dc0f3e005bd055c8db9ef6c0fec))

## [0.4.2](https://github.com/blockanalitica/chain-harvester/compare/v0.4.1...v0.4.2) (2023-08-28)


### Bug Fixes

* don't specify step size on mainnet and goerli ([#16](https://github.com/blockanalitica/chain-harvester/issues/16)) ([f720ef6](https://github.com/blockanalitica/chain-harvester/commit/f720ef6a31cff43c83eb452c27677dcb615dead9))

## [0.4.1](https://github.com/blockanalitica/chain-harvester/compare/v0.4.0...v0.4.1) (2023-08-28)


### Bug Fixes

* on retries, step is now devided isntead of static number ([#14](https://github.com/blockanalitica/chain-harvester/issues/14)) ([8dea0c8](https://github.com/blockanalitica/chain-harvester/commit/8dea0c89f4a50366adf4faa831b58c179413b669))

## [0.4.0](https://github.com/blockanalitica/chain-harvester/compare/v0.3.1...v0.4.0) (2023-08-28)


### Features

* generic event fetcher and decoder ([#12](https://github.com/blockanalitica/chain-harvester/issues/12)) ([2927abd](https://github.com/blockanalitica/chain-harvester/commit/2927abd6906d7123b5e57a26ef7ed034379e7755))

## [0.3.1](https://github.com/blockanalitica/chain-harvester/compare/v0.3.0...v0.3.1) (2023-08-24)


### Bug Fixes

* pypi publishing ([334b046](https://github.com/blockanalitica/chain-harvester/commit/334b04618767170ce3786ff2fd53d465156c3570))

## [0.3.0](https://github.com/blockanalitica/chain-harvester/compare/v0.2.0...v0.3.0) (2023-08-24)


### Features

* Add base chain, fetching events ([9526474](https://github.com/blockanalitica/chain-harvester/commit/95264740970af52bdd01b7957e4a9819925f85be))
* add ethereum mainnet network ([#5](https://github.com/blockanalitica/chain-harvester/issues/5)) ([0097a77](https://github.com/blockanalitica/chain-harvester/commit/0097a77a4b2a9b5dd335cf46196bef9226b60b66))
* Add multicall ([#3](https://github.com/blockanalitica/chain-harvester/issues/3)) ([575e851](https://github.com/blockanalitica/chain-harvester/commit/575e851cbecfd0b77655fd2eb98e8565b4f9a95c))
* Added Goerli support and changed how yield functions work ([#9](https://github.com/blockanalitica/chain-harvester/issues/9)) ([36eb3bc](https://github.com/blockanalitica/chain-harvester/commit/36eb3bcb17fff98b378f32312ea43a6a31d5ef63))
* use rpc_nodes for EthereumMainnetChain ([#7](https://github.com/blockanalitica/chain-harvester/issues/7)) ([8740ffe](https://github.com/blockanalitica/chain-harvester/commit/8740ffe42c49cce8ab26664e16955aa2b36bc7f6))


### Bug Fixes

* multicall ([#6](https://github.com/blockanalitica/chain-harvester/issues/6)) ([d14957c](https://github.com/blockanalitica/chain-harvester/commit/d14957c3ec2ccbc3d8a042cf6ff94ab9bcb50c19))

## [0.2.0](https://github.com/blockanalitica/chain-harvester/compare/v0.1.0...v0.2.0) (2023-08-06)


### Features

* add ethereum mainnet network ([#5](https://github.com/blockanalitica/chain-harvester/issues/5)) ([0097a77](https://github.com/blockanalitica/chain-harvester/commit/0097a77a4b2a9b5dd335cf46196bef9226b60b66))
* Add multicall ([#3](https://github.com/blockanalitica/chain-harvester/issues/3)) ([575e851](https://github.com/blockanalitica/chain-harvester/commit/575e851cbecfd0b77655fd2eb98e8565b4f9a95c))
* use rpc_nodes for EthereumMainnetChain ([#7](https://github.com/blockanalitica/chain-harvester/issues/7)) ([8740ffe](https://github.com/blockanalitica/chain-harvester/commit/8740ffe42c49cce8ab26664e16955aa2b36bc7f6))


### Bug Fixes

* multicall ([#6](https://github.com/blockanalitica/chain-harvester/issues/6)) ([d14957c](https://github.com/blockanalitica/chain-harvester/commit/d14957c3ec2ccbc3d8a042cf6ff94ab9bcb50c19))
