from qtpy.QtWidgets import QMainWindow

from pymodaq_gui.utils.custom_app import CustomApp
from pymodaq_gui.utils.utils import mkQApp
from pymodaq_gui.utils.dock import DockArea, Dock

from laser_risk_calculator.calculator.exposure import evaluate
from laser_risk_calculator.calculator.laser import Beam, Laser, LaserType


class LaserGui(CustomApp):
    """Interface autonome : saisie d'un laser à un faisceau et résumé de l'exposition.

    Elle ne contient aucune logique de calcul : tout passe par le cœur du paquet.
    """

    params = [
        {'title': 'Name:', 'name': 'name', 'type': 'str', 'value': '',
         'tip': 'The name of your laser'},
        {'title': 'Laser Type:', 'name': 'laser_type', 'type': 'list', 'limits': LaserType.names(),
         'value': LaserType.names()[0], 'tip': 'The type of your laser'},
        {'title': 'Pulse Duration:', 'name': 'pulse_duration', 'type': 'str', 'value': '',
         'tip': 'The duration of your laser in the string form: "100 fs"', 'visible': False},
        {'title': 'Wavelength:', 'name': 'wavelength', 'type': 'str', 'value': '',
         'tip': 'The wavelength of your laser in the string form: "515 nm"'},
        {'title': 'Power:', 'name': 'power', 'type': 'str', 'value': '',
         'tip': 'Continuous or average power: "5 mW"'},
        {'title': 'Beam diameter:', 'name': 'diameter', 'type': 'str', 'value': '',
         'tip': 'Beam diameter at the output: "0.7 mm"'},
        {'title': 'Divergence:', 'name': 'divergence', 'type': 'str', 'value': '',
         'tip': 'Full divergence: "1.2 mrad"'},
        {'title': 'Laser is:', 'name': 'laser_repr', 'type': 'text', 'value': '', 'readonly': True}
    ]

    def __init__(self, dockarea):

        super().__init__(dockarea)

        # init the object parameters
        self.setup_ui()

    def setup_docks(self):
        dock_laser = Dock('Laser Settings')
        self.dockarea.addDock(dock_laser)

        dock_laser.addWidget(self.settings_tree)

    def setup_actions(self):
        pass

    def connect_things(self):
        pass

    def value_changed(self, param):
        if param.name() == 'laser_type':
            self.settings.child('pulse_duration').show(param.value() == LaserType.Pulsed.name)

        optional = {key: self.settings[key] or None
                    for key in ('pulse_duration', 'power', 'diameter', 'divergence')}
        try:
            beam = Beam(laser_type=LaserType[self.settings['laser_type']],
                        wavelength=self.settings['wavelength'], **optional)
            laser = Laser(name=self.settings['name'], beams=[beam])
        except ValueError:
            return  # saisie incomplète ou invalide : on garde le texte précédent

        text = laser.model_dump_json(indent=2)
        try:
            result = evaluate(beam)
            text += f'\nEMP : {result.mpe:.3~P}\nDNRO : {result.nohd:.3~P}'
        except (NotImplementedError, ValueError) as e:
            text += f'\nExposition non calculée : {e}'
        self.settings.child('laser_repr').setValue(text)


def main():
    import sys
    app = mkQApp('Laser Risk')

    mainwindow = QMainWindow()
    mainwindow.setWindowTitle('laser Risk Calculator')
    dockarea = DockArea()
    mainwindow.setCentralWidget(dockarea)

    prog = LaserGui(dockarea)
    mainwindow.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
