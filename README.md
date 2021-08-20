# BuildBotStatusLight
Status Lights For the Build

This system connects to a [BuildBot](https://buildbot.net/) system and fetches the status of the builds and changes an
RGB globe or strip via an IR controller.

The IR controller is a USB Serial device called an [IR Toy](http://dangerousprototypes.com/docs/USB_IR_Toy_v2) from 
Dangerous Prototypes. Separate libraries are in place to abstract the hardware away from controlling the globes.
