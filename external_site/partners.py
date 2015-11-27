import re
from httplib import HTTPConnection

INNO_SITE = 'inno-terra.ru'
PENZA_SITE = 'pnzreg.ru'
BIPENZA_SITE = 'biznes-penza.ru'


def _fgroup(regex):
  return lambda data, flags=[]: re.search(regex, data, *flags).group(1)


def _re_grp(regex, grp, flags=[]):
  return lambda data: re.search(regex, data, *flags).group(grp)


def _get_page(site):
    conn = HTTPConnection(site)
    conn.request('GET', '/')
    data = conn.getresponse().read()
    return data


def _slice_info(data, start, stop):
    data = data[data.find(start):]
    return data[:data.find(stop)]


def _remove_tags(data):
    try:
        data = re.search(r'<.*>.*</.*>', data).group(0)
    except AtrributeError:
        return ''
    new_string = ''
    open_flag = True
    for i in data:
        if i == '<':
          open_flag = True
        elif i == '>':
          open_flag = False
          continue
        if not open_flag:
          new_string = new_string + i
    return new_string


def _get_info(dict_, site, slices, appends):
    data = _slice_info(_get_page(site), *slices)
    try:
        dict_[site] = []
        for i in appends:
            dict_[site].append(i(data))
    except AttributeError:
        dict_[site] = False
    finally:
      return


def _penza_news(dict_):
    # TODO: refactoring, change base to re_base
    base = lambda data, num: _fgroup(
          r'<a .*>(.*)</a>')(
          re.search(
              r'(<a .*>.*</a>).*(<a .*>.*</a>).*(<a .*>.*</a>)',
              data, re.DOTALL
          ).group(num)
    )
    _get_info(dict_, PENZA_SITE, ['id="front_news"','</table>'], [
        _re_grp(r'(\d+\.\d+\.\d{4}) \d+:\d+', 1),
        _re_grp(r'<img.*src="(.*)"></a>', 1),
        lambda data: base(data, 2),
        _re_grp(r'<a href="(.*)"><img', 1),
        lambda data: base(data, 3)
    ])


def _innotera_news(dict_):
    # TODO: refactoring, remove lambda, making more reading
    _get_info(dict_, INNO_SITE, ['views-row-first','views-row-2'], [
        _fgroup(r'.* (\d+.*, 20\d\d) - \d\d:\d\d'),
        lambda data: ".".join(_fgroup(
            r'.* src="(.*)" \w'
        )(data).split('"')[0].split(".thumbnail.")),
        lambda data: _fgroup(r'<a href="/node/\d+">(.*)</a>')(
            _fgroup(r'<div class="views-field-title">(.*)')(data, [re.DOTALL])
        ),
        _fgroup(r'(/node/\d+)'),
        lambda data: _remove_tags(_fgroup(
            r'<div class="views-field-teaser">(.*</p>)')(data, [re.DOTALL])
        )
    ])


def _bizpenza_news(dict_):
    re_base = lambda grp: _re_grp(
        r'<p class="news_title">.*<a href="(.*)" >(.*)</a>', grp, [re.DOTALL]
    ) 
    _get_info(dict_, BIPENZA_SITE, ['class="left_col"','class="right_col announce"'], [
        _re_grp(r'<span class="news_date">(.*)</span>', 1),
        _re_grp(r'<img.*src="(.*)" \w.*></a>', 1),
        re_base(2),
        re_base(1)
    ])


def get_partner_news():
  dict_ = {}
  for func in [_innotera_news, _penza_news, _bizpenza_news]:
    func(dict_)
  return dict_
