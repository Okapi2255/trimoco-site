# Deprecated: do not use. Business base is 20 Concord St, Lynbrook, NY 11563.
# The live pass is build/lynbrook.py (exec'd from build/build.py).
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lynbrook.py")).read(), globals())
