from languages.hu import LANG as HU


class LANG(HU):
  def delimiters(self):
    return {'--': super().delimiters()['–']}
