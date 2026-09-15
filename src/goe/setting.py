SCREEN_SIZE = 800*3, 600*3
FIXED_DT = 1/60
MAX_FRAMERATE = 144

CAM_SCALE_MIN = 2
CAM_SCALE_MAX = 40
CAM_MOVE_SPEED = 1000
CAM_SCALE_SPEED = 30

# Zypher
#CELL_TYPE = "fuzzy"
#BACKGROUND_COLOR = (240, 240, 240)
#CELL_ALIVE_COLOR = (198, 230, 251)
#CELL_BORN_COLOR = (0, 50, 170)       # Applies when zoomed to CELL_DEBUG_ZOOM
#CELL_DIED_COLOR = (30, 20, 20)       # Applies when zoomed to CELL_DEBUG_ZOOM
#CELL_DEBUG_ZOOM = 0.9                # Shows dead/born cells with color

# Standard
CELL_TYPE = "cell" # or "circle"
BACKGROUND_COLOR = (10, 10, 10)
CELL_ALIVE_COLOR = (0, 0, 170)
CELL_BORN_COLOR = (0, 50, 170)       # Applies when zoomed to CELL_DEBUG_ZOOM
CELL_DIED_COLOR = (30, 20, 20)       # Applies when zoomed to CELL_DEBUG_ZOOM
CELL_DEBUG_ZOOM = 0.9                # Shows dead/born cells with color

# Fancy
#CELL_TYPE = "bloom"
#BACKGROUND_COLOR = (10, 10, 20)
#CELL_ALIVE_COLOR = (0, 0, 100)        # Bloom color
#CELL_BORN_COLOR = (0x30, 0x60, 0x30)  # Nucleus color
#CELL_DIED_COLOR = (-1, -1, -1)        # Unused
#CELL_DEBUG_ZOOM = -1                  # Unused
