from languages.it import It


class Hu(It):
    def delimiters(self):
        return {'–': super().delimiters()['--']}
