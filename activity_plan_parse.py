# PanCam Activity Plan Parser
# Script to turn to parse activity plan tasks and actions and add the parameter mapping in the comments.

from os import unlink
from pathlib import Path
from itertools import zip_longest

# Constant Parameter List for Tasks and Actions

IMAGING_POS_PARAMS = (
    'PanPosition1',
    'TiltPosition1',
    'PanPosition2',
    'TiltPosition2',
    'PanPosition3',
    'TiltPosition3',
    'PanPosition4',
    'TiltPosition4',
    'PanPosition5',
    'TiltPosition5',
    'PanPosition6',
    'TiltPosition6',
    'PanPosition7',
    'TiltPosition7',
    'PanPosition8',
    'TiltPosition8',
)

IMAGING_WAC_POS_PARAMS = IMAGING_POS_PARAMS + (
    'PanPosition9',
    'TiltPosition9',
    'PanPosition10',
    'TiltPosition10',
)

IMAGING_BLOCK_ID_PARAMS = (
    'UTMblockID',
    'TMblockID'
)

IMAGING_WAC_AE_PARAMS = IMAGING_BLOCK_ID_PARAMS + (
    'WACIntTime',
    'WACAE_OTL',
    'WACAE_TARG',
    'WACAE_ROIX',
    'WACAE_ROIY',
    'WACAE_ROIW',
    'WACAE_ROIH',
    'WACAE_TOL',
    'WACAE_ITER'
)

IMAGING_WAC_PROCESSING_PARAMS = (
    'PanCam_subframeCoordX',
    'PanCam_subframeCoordY',
    'PanCam_subframeRows',
    'PanCam_subframeColumns',
    'superPixelSize',
    'mode',
    'UTMCriticality',
    'TMCriticality',
    'UTMDestination',
    'BackupFlag'
)

IMAGING_HRC_PROCESSING_PARAMS = (
    'PanCam_subframeCoordX',
    'PanCam_subframeCoordY',
    'PanCam_subframeRows',
    'PanCam_subframeColumns',
    'UTMCriticality',
    'TMCriticality',
    'UTMDestination',
    'BackupFlag'
)

IMAGING_HRC_PARAMS = (
    'IntTimeMin',
    'IntTimeMax',
    'SaturatedPixels',
    'Tolerance',
    'FocusWin_X',
    'FocusWin_Y',
    'FocusWin_Size',
    'Encoder_Value'
)

IMAGING_ISEM_PARAMS = (
    'UseISEM',
    'MODE'
)

IMAGING_WAC_STANDARD_PARAMS = ('WACNumPositions', ) \
    + IMAGING_WAC_POS_PARAMS \
    + IMAGING_WAC_AE_PARAMS \
    + IMAGING_WAC_PROCESSING_PARAMS

# Functions that scale parameter values


def calc_wac_int_time(val):
    return f"{int(val)+1} ms"


def calc_wac_otl(val):
    return f"{int(val)*16*100/(1024*1024):.4f}%"


def calc_wac_targ(val):
    if val == '0':
        return "no change in value"
    else:
        return f"{int(val)*4}"


def calc_wac_roi(val):
    return f"{int(val)*4}"


def calc_wac_roi_size(val):
    return f"{(int(val)+1)*4}"


def calc_wac_iter(val):
    return f"{int(val)+1}"


def calc_hrc_int(val):
    return f"{int(val)*0.350:.2f} ms"


def calc_gnc_image_time(val):
    return f"{int(val)*0.0008} ms"


def calc_panAbsAngle(val):
    if val == "0":
        return f"Not Used"
    else:
        return f"{float(val) * (400/65535) - 200:.2f} deg"


def calc_tiltAbsAngle(val):
    if val == "0":
        return f"Not Used"
    else:
        return f"{float(val) * (400/65535) - 200:.2f} deg"

# All the mapped parameters and the coding
VALUE_MAPPING = {
    'MechSafe': {'0': 'OFF', '1': 'ON'},
    'IsLast': {'0': 'FILES_KEPT_OPEN', '1': 'FILES_TO_BE_CLOSED'},
    'InitCam': {'1': 'WAC_L', '2': 'WAC_R', '3': 'HRC'},
    'CamSelection': {'0': 'NONE', '1': 'WAC_L', '2': 'WAC_R', '3': 'HRC'},
    'CamID': {'1': 'WAC_L', '2': 'WAC_R', '3': 'HRC'},
    'UTMblockID': {'2': 'SCI_CRI_LL',
                   '10': 'SCI_NCRI_LL'
                   },
    'WACExposureMode': {'1': 'AUTO_EXPOSURE', '2': 'SEMI_AUTO_EXPOSURE', '3': 'MANUAL_EXPOSURE'},
    'WACIntTime': calc_wac_int_time,
    'WACAE_OTL': calc_wac_otl,
    'WACAE_TARG': calc_wac_targ,
    'WACAE_ROIX': calc_wac_roi,
    'WACAE_ROIY': calc_wac_roi,
    'WACAE_ROIW': calc_wac_roi_size,
    'WACAE_ROIH': calc_wac_roi_size,
    'WACAE_ITER': calc_wac_iter,
    'UTMCriticality': {'2': 'NCSD', '3': 'CRITICAL'},
    'TMCriticality': {'2': 'NCSD', '3': 'CRITICAL'},
    'UTMDestination': {'0': 'NOT_SET', '1': 'SET'},
    'TMblockID': {'18': 'SCI_SF_CRI_LL',
                  '23': 'SCI_SF_CRI_8',
                  '24': 'SCI_SF_CRI_6',
                  '25': 'SCI_SF_CRI_4',
                  '26': 'SCI_SF_NCRI_LL'
                  },
    'mode': {'0': 'NONE', '1': 'DOWNSAMPLING', '2': 'BINNING', '3': 'ALL'},
    'BackupFlag': {'0': 'KEEP_RAW_DATA', '1': 'DELETE_RAW_DATA'},
    'WAC_ID': {'1': 'WAC_L', '2': 'WAC_R'},
    'FocusMode': {'1': 'AUTO_FOCUS', '2': 'MANUAL_FOCUS'},
    'FocusWin_Size': {'0': '256x256', '1': '128x128', '2': '64x64', '3': '32x32'},
    'HRCExposureMode': {'1': 'AUTO_EXPOSURE', '2': 'MANUAL_EXPOSURE'},
    'IntTimeMin': calc_hrc_int,
    'IntTimeMax': calc_hrc_int,
    'HRCIntTime': calc_hrc_int,

    # PanPositions
    'PanPosition1': calc_panAbsAngle,
    'TiltPosition1': calc_tiltAbsAngle,
    'PanPosition2': calc_panAbsAngle,
    'TiltPosition2': calc_tiltAbsAngle,
    'PanPosition3': calc_panAbsAngle,
    'TiltPosition3': calc_tiltAbsAngle,
    'PanPosition4': calc_panAbsAngle,
    'TiltPosition4': calc_tiltAbsAngle,
    'PanPosition5': calc_panAbsAngle,
    'TiltPosition5': calc_tiltAbsAngle,
    'PanPosition6': calc_panAbsAngle,
    'TiltPosition6': calc_tiltAbsAngle,
    'PanPosition7': calc_panAbsAngle,
    'TiltPosition7': calc_tiltAbsAngle,
    'PanPosition8': calc_panAbsAngle,
    'TiltPosition8': calc_tiltAbsAngle,
    'PanPosition9': calc_panAbsAngle,
    'TiltPosition9': calc_tiltAbsAngle,
    'PanPosition10': calc_panAbsAngle,
    'TiltPosition10': calc_tiltAbsAngle,
    # GNC_TakeImages
    'target_camera': {'0': 'LOCCAM', '1': 'NAVCAM'},
    'R_exposure_time': calc_gnc_image_time,
    'L_exposure_time': calc_gnc_image_time,
    'R_binning_mode': {'0': 'DISABLED', '1': 'ENABLED'},
    'L_binning_mode': {'0': 'DISABLED', '1': 'ENABLED'},
    'target_sensor': {'1': 'Right Sensor', '2': 'Left Sensor', '3': 'Both Sensors'},

    # MAST_PTU_MoveTo
    'panAbsAngle': calc_panAbsAngle,
    'tiltAbsAngle': calc_tiltAbsAngle
}


def _c(s):
    """Function to prefix comment symbol and 'pc_par' and adds newline when writing to output."""
    return f"#pc_par: {s} \n"


def read_file(file_path, output_file):
    """Function opens and starts reading through file lines"""

    task_functions = {
        "PanCam_GetImage": "Want to map to a function"
    }

    with open(file_path, 'r') as file:
        for line in file:
            # Parse each PanCam action
            process_line(line, output_file)

            output_file.write(line)


def process_line(line, output_file):
    """
    Function reads line, skips if a comment or blank. Then searches for PanCam task/action names.

    Valid task action names are given in the function map keys. If task/action name is matched the parameter value is
    then mapped using the VALUE_MAPPING and any functions. 
    """

    # Dict of each action/task name and function name used to lookup parameter names
    function_map = {
        "GNC_TakeImages": a_gnc_takeimages,
        "RV_Configure": a_rv_configure,
        "MAST_PTU_MoveTo": a_mast_ptu_moveto,
        "PanCam_Initialise": a_initialise,
        "PanCam_PIUSwitchOff": a_piu_switch_off,
        "PanCam_InitCam": a_init_cam,
        "PanCam_SwitchOn": a_switch_on,
        "PanCam_Enable": a_enable,
        "PanCam_GetImage": a_get_image,
        "PanCam_FilterSel": a_filter_sel,
        "PanCam_HRCfocus": a_hrc_focus,
        "PanCam_HRCexp": a_hrc_exp,
        "PanCam_MakeSafe": a_makesafe,
        "PANCAM_WAC_RR(": t_wac_rr,
        "PANCAM_WAC_RRGB": t_wac_rrgb,
        "PANCAM_WAC_Geol": t_wac_geol,
        "PANCAM_WAC_Solar": t_wac_solar,
        "PANCAM_HRC_ISEM_RGBnear": t_hrc_isem_rgb_near,
        "PANCAM_HRC_ISEM_RGBfar": t_hrc_isem_rgb_far,
        "PANCAM_HRC_SupRes": t_hrc_sup_res,
        "PANCAM_WAC_Calibration": t_wac_calibration,
        "PANCAM_HRC_Calibration": t_hrc_calibration
    }

    if any(a in ['#', '\n'] for a in line[0]):
        # Comment or blank line in file so ignore and continue
        return

    # Check to see if any of the function_map keys are in the line
    for task_action in function_map:
        if task_action in line:
            # First output two blank lines for easier ready
            output_file.write("\n\n")

            # Use corresponding function to get parameter names
            param_names = function_map[task_action](output_file)

            # Pull parameters from activity parenthesis
            param_values = get_params(line, param_names)

            # Write each parameter value pair on a new line
            for key, val in param_values.items():
                if key in VALUE_MAPPING:
                    val_mapper = VALUE_MAPPING[key]

                    if isinstance(val_mapper, dict):
                        # If dictionary simply get value from the key
                        val_map = val_mapper.get(val, '*VAL NOT FOUND*')
                    else:
                        # Assume function, pass as argument
                        val_map = val_mapper(val)

                    output_file.write(_c(f"{key}: {val} [{val_map}]"))
                else:
                    output_file.write(_c(f"{key}: {val}"))

            # Simply append with all dashes to look pretty in output
            output_file.write(_c(''.center(60, '-')))


def get_params(line, param_names):
    """Extract parameters from line string by removing all white space, splitting by '(' & ')' and then ','"""
    param_values = line.replace(' ', '') \
        .split('(', 1)[1] \
        .split(')', 1)[0] \
        .split(',')

    # If not exact expected values the *MISSING* keyword will apepar in output.
    return dict(zip_longest(param_names, param_values, fillvalue='*MISSING*'))

# List of all actions and the parameter mappings


def a_initialise(output_file):
    output_file.write(_c("Action: Initialise".center(60, '-')))

    param_names = (
        'Sol',
        'task_ID',
        'task_run_num'
    )

    return param_names


def a_piu_switch_off(output_file):
    output_file.write(_c("Action: PIUSwitchOff".center(60, '-')))

    param_names = (
        'MechSafe',
        'IsLast'
    )

    return param_names


def a_init_cam(output_file):
    output_file.write(_c("Action: InitCam".center(60, '-')))

    param_names = ('CamID', )

    return param_names


def a_switch_on(output_file):
    output_file.write(_c("Action: SwitchOn".center(60, '-')))

    param_names = ('CamSelection', )

    return param_names


def a_enable(output_file):
    output_file.write(_c("Action: Enable".center(60, '-')))

    param_names = ('CamSelection', )

    return param_names


def a_get_image(output_file):
    output_file.write(_c("Action: Get_Image".center(60, '-')))

    param_names = (
        'CamID',
        'UTMblockID',
        'WACExposureMode',
        'WACIntTime',
        'WACAE_OTL',
        'WACAE_TARG',
        'WACAE_ROIX',
        'WACAE_ROIY',
        'WACAE_ROIW',
        'WACAE_ROIH',
        'WACAE_TOL',
        'WACAE_ITER',
        'UTMCriticality',
        'TMCriticality',
        'UTMDestination',
        'TMblockID',
        'PanCam_subframeCoordX',
        'PanCam_subframeCoordY',
        'PanCam_subframeRows',
        'PanCam_subframeColumns',
        'superPixelSize',
        'mode',
        'BackupFlag'
    )
    return param_names


def a_filter_sel(output_file):
    output_file.write(_c("Action: FilterSel".center(60, '-')))

    param_names = (
        'WAC_ID',
        'Filter_Pos'
    )

    return param_names


def a_hrc_focus(output_file):
    output_file.write(_c("Action: HRCfocus".center(60, '-')))

    param_names = (
        'FocusMode',
        'FocusWin_X',
        'FocusWin_Y',
        'FocusWin_Size',
        'Encoder_Value'
    )

    return param_names


def a_hrc_exp(output_file):
    output_file.write(_c("Action: HRCexp".center(60, '-')))

    param_names = (
        'HRCExposureMode',
        'IntTimeMin',
        'IntTimeMax',
        'SaturatedPixels',
        'Tolerance',
        'HRCIntTime'
    )

    return param_names


def a_makesafe(output_file):
    output_file.write(_c("Action: MakeSafe".center(60, '-')))

    param_names = (None)

    return param_names


def a_gnc_takeimages(output_file):
    output_file.write(
        _c("Action: Rover Vehicle Take NavCam/LocCam Image".center(60, '-')))

    param_names = (
        'target_camera',
        'R_exposure_time',
        'L_exposure_time',
        'R_db_gain',
        'L_db_gain',
        'R_analog_gain',
        'L_analog_gain',
        'R_binning_mode',
        'L_binning_mode',
        'target_sensor',
        'R_imgFileName',
        'L_imgFileName',
        'R_MemPartition',
        'L_MemPar'
    )

    return param_names


def a_mast_ptu_moveto(output_file):
    output_file.write(_c("Action: Rover Move Mast Head".center(60, '-')))

    param_names = (
        'panAbsAngle',
        'tiltAbsAngle'
    )

    return param_names


def a_rv_configure(output_file):
    output_file.write(_c("Action: Rover Vehicle Configure".center(60, '-')))

    param_names = (
        'ADE_R1L1_Config Activate',
        'ADE_R2L2_Config Activate',
        'ADE_R1L2_Config Activate',
        'ADE_R2L1_Config Activate',
        'BEMA_STR_DRV_Config Activate',
        'DMA_PAN_TILT_Config Activate',
        'IMU_Config Activate',
        'SPW_Router_A_Config Activate',
        'SPW_Router_B_Config Activate',
        'COPM_Config Activate',
        'LOCCAM_Config Activate',
        'NAVCAM_Config Activate',
        'BEMA_DEP_Config Activate',
        'DMA_DEP_Config Activate',
        'SA_L_Primary_Config Activate',
        'SA_L_Secondary_Config Activate',
        'SA_R_Primary_Config Activate',
        'SA_R_Secondary_Config Activate',
        'HDRM_R_Board_Config Activate',
        'HDRM_L_Board_Config Activate'

    )

    return param_names



def t_wac_rr(output_file):
    output_file.write(_c("Task: WAC_RR".center(60, '-')))

    param_names = IMAGING_WAC_STANDARD_PARAMS

    return param_names


def t_wac_rrgb(output_file):
    output_file.write(_c("Task: WAC_RRGB".center(60, '-')))

    param_names = IMAGING_WAC_STANDARD_PARAMS

    return param_names


def t_wac_geol(output_file):
    output_file.write(_c("Task: WAC_Geol".center(60, '-')))

    param_names = IMAGING_WAC_STANDARD_PARAMS

    return param_names


def t_wac_solar(output_file):
    output_file.write(_c("Task: WAC_Solar".center(60, '-')))

    param_names = ('Iteration', ) \
        + IMAGING_WAC_POS_PARAMS \
        + IMAGING_WAC_AE_PARAMS \
        + IMAGING_WAC_PROCESSING_PARAMS \
        + ('Int_Time_L', 'Int_Time_R')

    return param_names


def t_hrc_isem_rgb_near(output_file):
    output_file.write(_c("Task: HRC_ISEM_RGBnear".center(60, '-')))

    param_names = ('HRCNumPositions', ) \
        + IMAGING_POS_PARAMS \
        + IMAGING_BLOCK_ID_PARAMS \
        + IMAGING_HRC_PROCESSING_PARAMS \
        + IMAGING_HRC_PARAMS \
        + IMAGING_ISEM_PARAMS

    return param_names


def t_hrc_isem_rgb_far(output_file):
    output_file.write(_c("Task: HRC_ISEM_RGBfar".center(60, '-')))

    param_names = ('HRCNumPositions', ) \
        + IMAGING_POS_PARAMS \
        + IMAGING_BLOCK_ID_PARAMS \
        + IMAGING_HRC_PROCESSING_PARAMS \
        + IMAGING_HRC_PARAMS \
        + IMAGING_ISEM_PARAMS

    return param_names


def t_hrc_sup_res(output_file):
    output_file.write(_c("Task: HRC_SupRes".center(60, '-')))

    param_names = ('PanPosition', 'TiltPosition') \
        + IMAGING_BLOCK_ID_PARAMS \
        + IMAGING_HRC_PROCESSING_PARAMS \
        + IMAGING_HRC_PARAMS

    return param_names


def t_wac_calibration(output_file):
    output_file.write(_c("Task: WAC_Calibration".center(60, '-')))

    param_names = IMAGING_WAC_AE_PARAMS \
        + IMAGING_WAC_PROCESSING_PARAMS

    return param_names


def t_hrc_calibration(output_file):
    output_file.write(_c("Task: HRC_Calibration".center(60, '-')))

    param_names = IMAGING_BLOCK_ID_PARAMS \
        + IMAGING_HRC_PROCESSING_PARAMS \
        + IMAGING_HRC_PARAMS

    return param_names


if __name__ == '__main__':
    input_file_path = Path(
        input("Type the path to the file which is to be processed: "))

    output_file_path = input_file_path.with_suffix(".parsed.txt")

    try:
        output_file_path.unlink()
    except:
        None

    output_file_path.touch()
    output_file = open(output_file_path, 'w')

    read_file(input_file_path, output_file)

    output_file.close()
