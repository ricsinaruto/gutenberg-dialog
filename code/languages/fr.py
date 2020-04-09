from languages.hu import Hu


class Fr(Hu):
    def delimiters(self):
        return {'--': super().delimiters()['–']}
