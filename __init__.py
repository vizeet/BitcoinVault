import json

jsonobj = json.load(open('transaction_config.json', 'rt'))

# defines globals here
g_nettype = jsonobj['Network Type']
g_mnemonic_code = [' '.join(mnemonic_code) for mnemonic_code in jsonobj['Mnemonic Codes']]
g_source_info = jsonobj['Source Info']
g_target_info = jsonobj['Target Info']
g_transaction_fees = jsonobj['Transaction Fees']
g_locktime = jsonobj['Locktime']
g_in_use_access_keys = jsonobj['In-use Access Keys']
g_used_access_keys = jsonobj['Used Access Keys']

__all__ = ['g_nettype', 'g_mnemonic_code', 'g_source_info', 'g_target_info', 'g_transaction_fees', 'g_locktime', 'g_in_use_access_keys', 'g_used_access_keys']
