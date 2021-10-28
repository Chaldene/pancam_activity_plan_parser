# pancam_activity_plan_parser
Quick script to parse the PanCam parameters for a rover activity plan. The majority of PanCam parameters are currently
parsed except for the UTM and TM block IDs.

If the number of parameters for a task or action does not match the expected
then the `*MISSING*` keyword will be added to the output.

If a value is provided but does not match expectation then the parsing will output `*VAL NOT FOUND*`.

Built using python 3.9. To execute simply run the script and provide the full path to the activity plan location.

## Examples

The file `PANCAM_SPR_TEST v4.txt` is an example of an input to the script and the file `PANCAM_SPR_TEST v4.parsed.txt`
is what can be expected when it has executed.
