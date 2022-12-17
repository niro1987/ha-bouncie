[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

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
[buymecoffee]: https://www.buymeacoffee.com/niro1987
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
