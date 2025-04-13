import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

from assistant.gui import AsistenteGUI

def main():
    app = AsistenteGUI()
    app.run()

if __name__ == '__main__':
    main()