# Control Panel LCD Data Decode via Microsoft Excel

This directory has files used to decode a capture of Canon Pixma MX340
control panel LCD update data, confirming the main board transmits the
entire frame as a 1-bit bitmap.

The process started with [the logic analyzer capture file](../control_panel_mainboard_communication/Canon%20MX340%20LCD%20sleep%20and%20wake.sal).

The main board to control panel communication was then [exported to a CSV file](./mx340_sleep_and_wake.csv).

Which was then [imported into Microsoft Excel](./mx340_sleep_and_wake.xlsx).

A little bit of Excel formula turned some spreadsheet cells into graph paper
pixels. A screen snip was taken for each of the five chunks [and roughly assembled](./canon%20pixma%20mx340%20control%20panel%20lcd%20excel%20cell%20fill%20raw.png).

That information was then brought into an image editor for some cropping,
transforming, and aligning.

![Excel graph paper stitch](./canon%20pixma%20mx340%20control%20panel%20lcd%20excel%20cell%20fill%20aligned.png)

This matches up well to what I see on screen.

![Control panel LCD matches stitch](./canon%20pixma%20mx340%20control%20panel%20lcd%20real%20relative%20to%20excel%20cell%20fill.jpg)
