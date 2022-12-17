[![GitHub Release][releases-shield]][releases]
[![License][license-shield]][license]
[![Project Maintenance][user_profile-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]
[![hacs_badge][hacs-custom]][hacs]

_Component to integrate with [Bouncie][bouncie]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`device_tracker` | Vehicle tracker.
`sensor` | Odometer, Fuel Level, Speed sensor.

![bouncie][bouncieimg]

{% if not installed %}
## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Bouncie".

{% endif %}


## Configuration is done in the UI

<!---->

***

[bouncie]: https://github.com/niro1987/ha-bouncie
[bouncieimg]: logo.png
[user_profile]: https://github.com/niro1987
[user_profile-shield]: https://img.shields.io/badge/maintainer-Niels%20Perfors%20%40niro1987-blue.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/niro1987
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[license]: https://github.com/niro1987/ha-bouncie/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/niro1987/ha-bouncie.svg?style=for-the-badge
[releases]: https://github.com/niro1987/ha-bouncie/releases
[releases-shield]: https://img.shields.io/github/release/niro1987/ha-bouncie.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[hacs-custom]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
