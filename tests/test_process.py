import process


def test_parse_cmd():
    assert ('sleep', '1') == process.Process._parse_cmd('sleep 1')
    assert ('whoami', '') == process.Process._parse_cmd('whoami')
    assert ('"/my\'nice path\'/with chars"', ' 1 2 \'24\'') == \
           process.Process._parse_cmd('"/my\'nice path\'/with chars" 1 2 \'24\'')
    assert ('\'/my"nice path"/with chars\'', ' 1 2 "24"') == \
           process.Process._parse_cmd('\'/my"nice path"/with chars\' 1 2 "24"')
