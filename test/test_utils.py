__author__ = 'rohe0002'

from idpproxy import utils

spec = ["file:../config/secrets.example"]

ci = utils.ConsumerInfo(spec)

key, sec = ci("Google", "foobar")

assert key == "lingon"
assert sec == "aaaaa"