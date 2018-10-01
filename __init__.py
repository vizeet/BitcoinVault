import json

jsonobj = json.load(open('transaction_config.json', 'rt'))

# defines globals here
g_nettype = jsonobj['Network Type']
g_mnemonic_code = ' '.join(jsonobj['Mnemonic Code'])
g_source_info = jsonobj['Source Info']
g_change_info = jsonobj['Change Info']
g_target_info = jsonobj['Target Info']
g_transaction_fees = jsonobj['Transaction Fees']
g_locktime = jsonobj['Locktime']

__all__ = ['g_nettype', 'g_mnemonic_code', 'g_source_info', 'g_change_info', 'g_target_info', 'g_transaction_fees', 'g_locktime']
