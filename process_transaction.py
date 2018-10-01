import hd_wallet
import json
import pubkey_address
import binascii
from utility_adapters import leveldb_utils
from functools import reduce
from utility_adapters import hash_utils
import ecdsa
from __init__ import g_nettype, g_mnemonic_code, g_source_info, g_change_info, g_target_info, g_transaction_fees, g_locktime
from utility_adapters import script_utils
from utility_adapters import block_utils
from utils.opcode_declarations import *

#my_salt = 'test'
my_salt = ''

N = (1 << 256) - 0x14551231950B75FC4402DA1732FC9BEBF

def get_p2wpkh_address(access_key: str):
        global g_nettype, g_mnemonic_code
        print('mnemonic code = %s' % g_mnemonic_code)
        seed_b = hd_wallet.generateSeedFromStr(g_mnemonic_code, "mnemonic" + my_salt)
        privkey_i, pubkey_b = hd_wallet.generatePrivkeyPubkeyPair(access_key, seed_b, True)
        privkey_wif = pubkey_address.privkeyHex2Wif(privkey_i, g_nettype, True)
        pubkey_s = bytes.decode(binascii.hexlify(pubkey_b))
        address_s = pubkey_address.pubkey2segwitaddr(pubkey_b, g_nettype)
        h_b = pubkey_address.address2hash(address_s)
        h_s = bytes.decode(binascii.hexlify(h_b))
        #print('hash160 of address = %s' % bytes.decode(binascii.hexlify(h_b)))
        return privkey_wif, pubkey_s, h_s, address_s

def get_p2sh_p2wpkh_address(access_key: str):
        global g_nettype, g_mnemonic_code
        print('mnemonic code = %s' % g_mnemonic_code)
        seed_b = hd_wallet.generateSeedFromStr(g_mnemonic_code, "mnemonic" + my_salt)
        privkey_i, pubkey_b = hd_wallet.generatePrivkeyPubkeyPair(access_key, seed_b, True)
        privkey_wif = pubkey_address.privkeyHex2Wif(privkey_i, g_nettype, True)
        pubkey_s = bytes.decode(binascii.hexlify(pubkey_b))
        address_s = pubkey_address.pubkey2segwitaddr(pubkey_b, g_nettype)
        h_b = pubkey_address.address2hash(address_s)
        h_s = bytes.decode(binascii.hexlify(h_b))
        script_b = b'\x00\x14' + h_b
        address_s = pubkey_address.redeemScript2address(script_b, g_nettype)
        print('P2SH-P2WPKH Address = %s, script = %s' % (address_s, bytes.decode(binascii.hexlify(script_b))))
        return privkey_wif, pubkey_s, h_s, address_s

def get_p2sh_witness_redeem_script(hash160_s: str, size: int):
        script_s = "00%x%s" % (size, hash160_s)
        return script_s

def get_redeem_script_from_pubkey_list(pubkey_list: list, unlock_key_threshold: int):
        print('pubkey list = %s' % pubkey_list)
        encoded_opcode = script_utils.encodeOpN(unlock_key_threshold)
        print('encoded opcode = %x for int = %d' % (encoded_opcode, unlock_key_threshold))
        redeem_script_b = bytes([encoded_opcode]) + reduce(lambda x, y: x + y, [bytes([len(binascii.unhexlify(pubkey))]) + binascii.unhexlify(pubkey) for pubkey in pubkey_list]) + bytes([script_utils.encodeOpN(len(pubkey_list)), OP_CHECKMULTISIG])
        print('redeem_script = %s' % bytes.decode(binascii.hexlify(redeem_script_b)))
        return redeem_script_b

def get_p2sh_address_from_pubkey_list(pubkey_list: list, unlock_key_threshold: int):
        redeem_script_b = get_redeem_script_from_pubkey_list(pubkey_list, unlock_key_threshold)
        address = pubkey_address.redeemScript2address(redeem_script_b, g_nettype)
        return address

def get_p2wsh_address_from_pubkey_list(pubkey_list: list, unlock_key_threshold: int):
        redeem_script_b = get_redeem_script_from_pubkey_list(pubkey_list, unlock_key_threshold)
        witprog = hash_utils.sha256(redeem_script_b)
        address = pubkey_address.hash2segwitaddr(witprog, g_nettype)
        return address

def get_p2sh_p2wsh_address_from_pubkey_list(pubkey_list: list, unlock_key_threshold: int):
        redeem_script_b = get_redeem_script_from_pubkey_list(pubkey_list, unlock_key_threshold)
        witprog = hash_utils.sha256(redeem_script_b)
        p2sh_redeem_script_b = b'\x00' + bytes([len(witprog)]) + witprog
        address = pubkey_address.redeemScript2address(p2sh_redeem_script_b, g_nettype)
        return address

def get_p2sh_keymaplist(access_key_list: str):
        global g_nettype, g_mnemonic_code
        print('mnemonic code = %s' % g_mnemonic_code)
        seed_b = hd_wallet.generateSeedFromStr(g_mnemonic_code, "mnemonic" + my_salt)
        keylist = []
        for access_key in access_key_list:
                privkey_i, pubkey_b = hd_wallet.generatePrivkeyPubkeyPair(access_key, seed_b, True)
                privkey_wif = pubkey_address.privkeyHex2Wif(privkey_i, True, True)
                pubkey_s = bytes.decode(binascii.hexlify(pubkey_b))
                address_s = pubkey_address.pubkey2address(pubkey_b, nettype = g_nettype, is_segwit = False)
                h_b = pubkey_address.address2hash(address_s)
                h_s = bytes.decode(binascii.hexlify(h_b))
                keylist.append({'privkey': privkey_wif, 'pubkey': pubkey_s, 'hash160': h_s, 'addess': address_s})
        return keylist

def get_p2wsh_keymaplist(access_key_list: str):
        global g_nettype, g_mnemonic_code
        print('mnemonic code = %s' % g_mnemonic_code)
        seed_b = hd_wallet.generateSeedFromStr(g_mnemonic_code, "mnemonic" + my_salt)
        keylist = []
        for access_key in access_key_list:
                privkey_i, pubkey_b = hd_wallet.generatePrivkeyPubkeyPair(access_key, seed_b, True)
                privkey_wif = pubkey_address.privkeyHex2Wif(privkey_i, True, True)
                pubkey_s = bytes.decode(binascii.hexlify(pubkey_b))
                address_s = pubkey_address.pubkey2address(pubkey_b, nettype = g_nettype, is_segwit = True)
                h_b = pubkey_address.address2hash(address_s)
                h_s = bytes.decode(binascii.hexlify(h_b))
                keylist.append({'privkey': privkey_wif, 'pubkey': pubkey_s, 'hash160': h_s, 'addess': address_s})
        return keylist

def get_p2pkh_address(access_key: str):
        global g_nettype, g_mnemonic_code
        print('mnemonic code = %s' % g_mnemonic_code)
        seed_b = hd_wallet.generateSeedFromStr(g_mnemonic_code, "mnemonic" + my_salt)
        privkey_i, pubkey_b = hd_wallet.generatePrivkeyPubkeyPair(access_key, seed_b, True)
        privkey_wif = pubkey_address.privkeyHex2Wif(privkey_i, True, True)
        pubkey_s = bytes.decode(binascii.hexlify(pubkey_b))
        address_s = pubkey_address.pubkey2address(pubkey_b, nettype = g_nettype, is_segwit = False)
        h_b = pubkey_address.address2hash(address_s)
        h_s = bytes.decode(binascii.hexlify(h_b))
        #print('hash160 of address = %s' % h_s)
        #return privkey_wif, pubkey_s, h_s, address_s
        return {address_s: {'Public Key': pubkey_s, 'Private Key': privkey_wif, 'Hash 160': h_s}}

def swap_endian_bytes(in_b: bytes):
        out_b = in_b[::-1]
        return out_b

# Funding Address is used, returns list of transactions required
def get_utxos_for_address(addresses: list, amount: float):
        global g_nettype
        print('XXXXXXXXXXXXX addresses = %s' % addresses)
        ldb_adapter = leveldb_utils.LevelDBAdapter(g_nettype)
        utxos = ldb_adapter.getRequiredTxnsForAmount(addresses, amount)
        print('utxos = %s' % utxos)
        return utxos

#def get_utxos_for_address_p2wpkh(addresses: list, amount: float):
#        global g_nettype
#        utxos = leveldb_utils.getRequiredTxnsForAmount(addresses, amount, g_nettype)
#        print('utxos = %s' % utxos)
#        return utxos
#
#def get_utxos_for_address_p2sh(addresses: list, amount: float):
#        global g_nettype
#        utxos = leveldb_utils.getRequiredTxnsForAmount(addresses, amount, g_nettype)
#        print('utxos = %s' % utxos)
#        return utxos
#
#def get_utxos_for_address_p2wsh(addresses: list, amount: float):
#        global g_nettype
#        utxos = leveldb_utils.getRequiredTxnsForAmount(addresses, amount, g_nettype)
#        print('utxos = %s' % utxos)
#        return utxos

def get_funding_address_keys():
        global g_source_info
        keymap_list = []
        access_key_list = [src['Access Key'] for src in g_source_info['P2WPKH'] if 'Access Key' in src]
        for access_key in access_key_list:
                keymap = {}
                keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address'] = get_p2wpkh_address(access_key)
                print('privkey = %s, pubkey = %s, hash160 = %s, address = %s' % (keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address']))
                keymap_list.append(keymap)

        access_key_list = [src['Access Key'] for src in g_source_info['P2SH-P2WPKH'] if ('Access Key' in src)]
        for access_key in access_key_list:
                keymap = {}
                keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address']  = get_p2sh_p2wpkh_address(access_key)
                print('privkey = %s, pubkey = %s, hash160 = %s, address = %s' % (keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address']))
                keymap_list.append(keymap)

        access_key_list = [src['Access Key'] for src in g_source_info['P2PKH'] if ('Access Key' in src)]
        for access_key in access_key_list:
                keymap = {}
                keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address'] = get_p2pkh_address(access_key)
                print('privkey = %s, pubkey = %s, hash160 = %s, address = %s' % (keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address']))
                keymap_list.append(keymap)

        print('YYYYYYYYYYYYYYYYYYY keymap_list = %s' % keymap_list)
        return keymap_list

def get_funding_address_keys_p2wsh():
        global g_source_info
        keymaplist_list = []
        access_keys_list = [src for src in g_source_info['P2WSH'] if 'Access Keys' in src]
        print('access_keys_list = %s' % access_keys_list)
        for access_keys in access_keys_list:
                keymaplist  = {'Keymap List': get_p2wsh_keymaplist(access_keys['Access Keys']), 'Lock Key Count': access_keys['Lock Key Count'], 'Unlock Key Threshold': access_keys['Unlock Key Threshold']}
                print('keymaplist = %s' % keymaplist)
                keymaplist_list.append(keymaplist)

        print('KKKKKKKKKKKKKKKKK keymaplist_list = %s' % keymaplist_list)
        return keymaplist_list

def get_funding_address_keys_p2sh():
        global g_source_info
        keymaplist_list = []
        access_keys_list = [src for src in g_source_info['P2SH'] if 'Access Keys' in src]
        print('access_keys_list = %s' % access_keys_list)
        for access_keys in access_keys_list:
                keymaplist  = {'Keymap List': get_p2sh_keymaplist(access_keys['Access Keys']), 'Lock Key Count': access_keys['Lock Key Count'], 'Unlock Key Threshold': access_keys['Unlock Key Threshold']}
                print('keymaplist = %s' % keymaplist)
                keymaplist_list.append(keymaplist)

        print('KKKKKKKKKKKKKKKKK keymaplist_list = %s' % keymaplist_list)
        return keymaplist_list

def get_funding_address_keys_p2sh_p2wsh():
        global g_source_info
        keymaplist_list = []
        access_keys_list = [src for src in g_source_info['P2WSH'] if 'Access Keys' in src]
        print('access_keys_list = %s' % access_keys_list)
        for access_keys in access_keys_list:
                keymaplist  = {'Keymap List': get_p2wsh_keymaplist(access_keys['Access Keys']), 'Lock Key Count': access_keys['Lock Key Count'], 'Unlock Key Threshold': access_keys['Unlock Key Threshold']}
                print('keymaplist = %s' % keymaplist)
                keymaplist_list.append(keymaplist)

        print('KKKKKKKKKKKKKKKKK keymaplist_list = %s' % keymaplist_list)
        return keymaplist_list

def get_funding_address_keys_p2pkh():
        global g_source_info
        keymap_list = []
        access_key_list = [src['Access Key'] for src in g_source_info['P2PKH'] if 'Access Key' in src]
        for access_key in access_key_list:
                keymap = {}
                keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address']  = get_p2pkh_address(access_key)
                print('privkey = %s, pubkey = %s, hash160 = %s, address = %s' % (keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address']))
                keymap_list.append(keymap)

        print('YYYYYYYYYYYYYYYYYYY keymap_list = %s' % keymap_list)
        return keymap_list

def get_funding_address_keys_p2wpkh():
        global g_source_info
        keymap_list = []
        access_key_list = [src['Access Key'] for src in g_source_info['P2WPKH'] if 'Access Key' in src]
        for access_key in access_key_list:
                keymap = {}
                keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address'] = get_p2wpkh_address(access_key)
                print('privkey = %s, pubkey = %s, hash160 = %s, address = %s' % (keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address']))
                keymap_list.append(keymap)

        print('YYYYYYYYYYYYYYYYYYY keymap_list = %s' % keymap_list)
        return keymap_list

def get_funding_address_keys_p2sh_p2wpkh():
        global g_source_info
        keymap_list = []
        access_key_list = [src['Access Key'] for src in g_source_info['P2SH-P2WPKH'] if 'Access Key' in src]
        for access_key in access_key_list:
                keymap = {}
                keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address']  = get_p2sh_p2wpkh_address(access_key)
                keymap['script'] = get_p2sh_witness_redeem_script(keymap['hash160'], 0x14)
                print('privkey = %s, pubkey = %s, hash160 = %s, address = %s' % (keymap['privkey'], keymap['pubkey'], keymap['hash160'], keymap['address']))
                keymap_list.append(keymap)

        print('YYYYYYYYYYYYYYYYYYY keymap_list = %s' % keymap_list)
        return keymap_list

def get_change_address_hash():
        global g_change_info

        if g_change_info['Address Type'] == 'P2WPKH':
                access_key = g_change_info['Access Key']
                privkey, pubkey, witness_program, address = get_p2wpkh_address(access_key)
                witness_program_b = binascii.unhexlify(witness_program)
        elif g_change_info['Address Type'] == 'P2SH-P2WPKH':
                access_key = g_change_info['Access Key']
                privkey, pubkey, witness_program, address = get_p2sh_p2wpkh_address(access_key)
        elif g_change_info['Address Type'] == 'P2PKH':
                access_key = g_change_info['Access Key']
                privkey, pubkey, witness_program, address = get_p2pkh_address(access_key)
        elif g_change_info['Address Type'] == 'P2SH':
                access_keys_list = g_change_info['Access Keys']
                keymaplist = get_p2sh_keymaplist(access_keys_list)
        print('change witness_program = %s, change_address = %s' % (witness_program, address))
        return witness_program_b, address

def btc2satoshis(btc: float):
        return int(btc * (10**8))

def satoshis2btc2(satoshis: int):
        return satoshis / (10**8)

def get_required_amount():
        global g_target_info, g_transaction_fees
        input_amount = reduce(lambda x, y: x + y, [tval['Amount'] for tval in g_target_info])
        required_amount = input_amount + g_transaction_fees
        return required_amount

address_type_prefix_map = {
        'segwit': ['bc1', 'tb1', 'bcrt1'],
        'script': ['3', '2'],
        'pre_segwit': ['1', 'm', 'n']
}

def get_default_script(h: bytes, address_type: str):
        if address_type == 'pre_segwit': # P2PKH
                # OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
                script_b = bytes([0x76, 0xa9, 0x14]) + h + bytes([0x88, 0xac])
        elif address_type == 'segwit': #P2WPKH
                # OP_0 <witness-program>
                script_b = bytes([0x00, 0x14]) + h
        elif address_type == 'script': # P2SH
                # HASH160 <scriptHash> EQUAL
                script_b = bytes([0xa9, 0x14]) + h + bytes([0x87])
        return script_b

def get_address_type(address: str):
        address_type = [k for k, v in address_type_prefix_map.items() if address.startswith(tuple(v))][0]
        return address_type

def get_default_locking_script(address: str):
        address_type = get_address_type(address)
        print('address type = %s' % address_type)
        h_b = pubkey_address.address2hash(address)
        h_s = bytes.decode(binascii.hexlify(h_b))
        print('hash160 of pubkey = %s from address = %s' % (h_s, address))
        script_b = get_default_script(h_b, address_type)
        return script_b
        
def btc2bytes(btc: float):
        satoshis = int(btc * (10**8))
        print('satoshis = %s' % satoshis)
        hex_b = binascii.unhexlify('%016x' % satoshis)[::-1]
        return hex_b

def locktime2bytes(locktime: int):
        hex_b = binascii.unhexlify('%08x' % locktime)[::-1]
        return hex_b

def prepare_txn_inputs_p2sh(utxo_list: list, preimage_list: list, address_privkeys_map: dict, address_pubkeys_map: dict, address_unlock_key_threshold_map: dict):
        global g_locktime
        input_count = len(utxo_list)
        in_txn = bytes([input_count])
        sequence = None
        #for utxo, preimage in zip(utxo_list, preimage_list):
        #count = len(utxo_list)
        #print('GGGGGGGGG utxo length = %d' % count)
        for utxo, preimage in zip(utxo_list, preimage_list):
                privkey_list = address_privkeys_map[utxo['address']]
                pubkey_list = address_pubkeys_map[utxo['address']]
                unlock_key_threshold = address_unlock_key_threshold_map[utxo['address']]
                scriptsig_b = bytes([OP_0])
                for key_index in range(unlock_key_threshold):
                        sig_b = sign_txn_input(preimage, privkey_list[key_index])
                        sig_size_b = bytes([len(sig_b)])
                        scriptsig_b += sig_size_b + sig_b
                redeem_script_b = bytes([script_utils.encodeOpN(unlock_key_threshold)])
                for pubkey in pubkey_list:
                        pubkey_b = binascii.unhexlify(pubkey)
                        pubkey_size_b = bytes([len(pubkey_b)])
                        redeem_script_b += pubkey_size_b + pubkey_b
                redeem_script_b += bytes([script_utils.encodeOpN(len(pubkey_list))])
                redeem_script_b += bytes([OP_CHECKMULTISIG])
                #redeem_script_size_b = bytes([len(redeem_script_b)])
                redeem_script_size_b = script_utils.encode_pushdata(len(redeem_script_b))
                scriptsig_b += redeem_script_size_b + redeem_script_b
                scriptsig_size_b = block_utils.encode_var_length_bytes(len(scriptsig_b))
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                in_txn += swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1] + scriptsig_size_b + scriptsig_b + sequence
        return in_txn

def prepare_txn_inputs_p2pkh(utxo_list: list, preimage_list: list, address_privkey_map: dict, address_pubkey_map: dict):
        global g_locktime
        input_count = len(utxo_list)
        in_txn = bytes([input_count])
        sequence = None
        for utxo, preimage in zip(utxo_list, preimage_list):
                sig_b = sign_txn_input(preimage, address_privkey_map[utxo['address']])
                sig_size_b = bytes([len(sig_b)])
                scriptsig_b = sig_size_b + sig_b
                pubkey_b = binascii.unhexlify(address_pubkey_map[utxo['address']])
                pubkey_size_b = bytes([len(pubkey_b)])
                scriptsig_b += pubkey_size_b + pubkey_b
                scriptsig_size_b = bytes([len(scriptsig_b)])
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                in_txn += swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1] + scriptsig_size_b + scriptsig_b + sequence
        return in_txn

def prepare_txn_inputs_bare_witness(utxo_list: list):
        global g_locktime
        input_count = len(utxo_list)
        in_txn = bytes([input_count])
        sequence = None
        for utxo in utxo_list:
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                scriptsig_size = b'\x00' # for bare witness
                in_txn += swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1] + scriptsig_size + sequence
        return in_txn

def prepare_txn_inputs_p2sh_p2wsh(utxo_list: list, address_pubkeys_map: dict, address_unlock_key_threshold_map: dict):
        global g_locktime
        input_count = len(utxo_list)
        in_txn = bytes([input_count])
        sequence = None
        for utxo in utxo_list:
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                sha256_b = hash_utils.sha256(get_redeem_script_from_pubkey_list(address_pubkeys_map[utxo['address']], address_unlock_key_threshold_map[utxo['address']]))
                redeem_script_b = b'\x00\x20' + sha256_b
                redeem_script_size_b = script_utils.encode_pushdata(len(redeem_script_b))
                scriptsig_b = redeem_script_size_b + redeem_script_b
                scriptsig_size_b = block_utils.encode_var_length_bytes(len(scriptsig_b))
                in_txn += swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1] + scriptsig_size_b + scriptsig_b + sequence
        return in_txn

def prepare_txn_inputs(utxo_list: list):
        global g_locktime
        input_count = len(utxo_list)
        in_txn = bytes([input_count])
        sequence = None
        for utxo in utxo_list:
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                scriptsig_size = b'\x00'
                in_txn += swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1] + scriptsig_size + sequence
        return in_txn

def prepare_txn_inputs_p2sh_p2wpkh(utxo_list: list, address_script_map: dict):
        global g_locktime
        input_count = len(utxo_list)
        in_txn = bytes([input_count])
        sequence = None
        for utxo in utxo_list:
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                #scriptsig_size = b'\x00' # for bare witness
                address_s = pubkey_address.sh2address(binascii.unhexlify(utxo['hash160']), g_nettype)
                script_b = binascii.unhexlify(address_script_map[address_s])
                scriptsig = bytes([len(script_b)]) + script_b # for p2sh witness
                scriptsig_size = bytes([len(scriptsig)]) # for p2sh witness
                in_txn += swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1] + scriptsig_size + scriptsig + sequence
        return in_txn

def get_input_satoshis(utxo_list: list):
        input_satoshis = reduce(lambda x,y: x+y, [utxo['value'] for utxo in utxo_list])
        return input_satoshis

def prepare_txn_outs(utxo_list: list, req_amount: float):
        global g_target_info, g_transaction_fees
        target_count = len(g_target_info)
        out_count = target_count + 1
        input_btc = get_input_satoshis(utxo_list) / (10 ** 8)
        print('input_btc = %.8f' % input_btc)
        change_btc = input_btc - req_amount
        print('transaction fees = %.8f' % g_transaction_fees)
        print('required amount = %.8f' % req_amount)
        print('change_btc = %.8f' % change_btc)

        out_txn = bytes([out_count])
        for target in g_target_info:
                amount_b = btc2bytes(target['Amount'])
                address = target['Address']
                script_b = get_default_locking_script(address)
                script_size_b = bytes([len(script_b)])
                out_txn += amount_b + script_size_b + script_b
        change_b = btc2bytes(change_btc)
        change_witness_program_b, change_address = get_change_address_hash()
        size_change_witness_program_b = bytes([len(change_witness_program_b)])
        change_witness_version_b = b'\x00'
        size_change_script_b = bytes([len(change_witness_program_b) + len(change_witness_version_b) + 1])
        out_txn += change_b + size_change_script_b + change_witness_version_b + size_change_witness_program_b + change_witness_program_b
        return out_txn

def prepare_raw_txn(utxo_list: list):
        global g_locktime
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        req_amount = get_required_amount()
        print('required amount = %.8f' % req_amount)
        keymap_list = get_funding_address_keys()
        address_list = [keymap['address'] for keymap in keymap_list]
        print('address_list = %s' % address_list)
        utxo_list = get_utxos_for_address(address_list, req_amount)
        txnin = prepare_txn_inputs(utxo_list)
        print('txnin = %s' % bytes.decode(binascii.hexlify(txnin)))
        txnout = prepare_txn_outs(utxo_list, req_amount)
        print('txnout = %s' % bytes.decode(binascii.hexlify(txnout)))
        locktime_b = locktime2bytes(g_locktime)
        return version + txnin + txnout + locktime_b

def get_hash_prevouts(utxo_list: list):
        prevouts = b''
        for utxo in utxo_list:
                prevouts += swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1]
        print('prevouts = %s' % bytes.decode(binascii.hexlify(prevouts)))
        return hash_utils.hash256(prevouts) 

def get_hash_sequence(utxo_list: list):
        global g_locktime
        sequence = None
        concatenated_sequences = b''
        for utxo in utxo_list:
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                concatenated_sequences += sequence
        print('concatenated sequence = %s' % bytes.decode(binascii.hexlify(concatenated_sequences)))
        return hash_utils.hash256(concatenated_sequences) 

def get_hash_outs(utxo_list):
        global g_target_info
        out_txn = b''
        req_amount = get_required_amount()
        input_btc = get_input_satoshis(utxo_list) / (10 ** 8)
        print('input_btc = %.8f' % input_btc)
        change_btc = input_btc - req_amount
        for target in g_target_info:
                amount_b = btc2bytes(target['Amount'])
                address = target['Address']
                script_b = get_default_locking_script(address)
                script_size_b = bytes([len(script_b)])
                out_txn += amount_b + script_size_b + script_b
        change_b = btc2bytes(change_btc)
        change_witness_program_b, change_address = get_change_address_hash()
#        change_witness_version_b = b'\x00'
#        size_change_script_b = bytes([len(change_witness_program_b) + len(change_witness_version_b) + 1])
#        out_txn += change_b + size_change_script_b + change_witness_version_b + bytes([len(change_witness_program_b)]) + change_witness_program_b
        size_change_witness_program_b = bytes([len(change_witness_program_b)])
        change_witness_version_b = b'\x00'
        size_change_script_b = bytes([len(change_witness_program_b) + len(change_witness_version_b) + 1])
        out_txn += change_b + size_change_script_b + change_witness_version_b + size_change_witness_program_b + change_witness_program_b
        return hash_utils.hash256(out_txn)

def get_preimage_list_p2sh(utxo_list: list, address_pubkeys_map: dict, address_unlock_key_threshold_map: dict):
        global g_locktime
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        req_amount = get_required_amount()
        print('required amount = %.8f' % req_amount)
        txnin = prepare_txn_inputs(utxo_list)
        print('txnin = %s' % bytes.decode(binascii.hexlify(txnin)))
        txnout = prepare_txn_outs(utxo_list, req_amount)
        print('txnout = %s' % bytes.decode(binascii.hexlify(txnout)))
        locktime_b = locktime2bytes(g_locktime)
        sighash_all = binascii.unhexlify('%08x' % 0x01)[::-1]

        preimage_list = []
        sequence = None
        n_inputs = txnin[0:1]
        counter = 0
        for utxo in utxo_list:
                address = utxo['address']
                redeem_script_b = get_redeem_script_from_pubkey_list(address_pubkeys_map[address], address_unlock_key_threshold_map[address])
                #hash160_b = binascii.unhexlify(utxo['hash160'])
                #prev_scriptpubkey_b = bytes([0xa9, len(hash160_b)]) + hash160_b + bytes([0x87])
                redeem_script_size_b = bytes([len(redeem_script_b)])
                index = (counter * (32 + 4 + 1 + 4)) + 32 + 4 
                #inputs = txnin[1:index + 1] + prev_scriptpubkey_size_b + prev_scriptpubkey_b + txnin[index + 2:]
                inputs = txnin[1:index + 1] + redeem_script_size_b + redeem_script_b + txnin[index + 2:]
                preimage = version + n_inputs + inputs + txnout + locktime_b + sighash_all
                preimage_list.append(preimage)
                counter += 1
        return preimage_list

def get_preimage_list_p2pkh(utxo_list: list):
        global g_locktime
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        req_amount = get_required_amount()
        print('required amount = %.8f' % req_amount)
        txnin = prepare_txn_inputs(utxo_list)
        print('txnin = %s' % bytes.decode(binascii.hexlify(txnin)))
        txnout = prepare_txn_outs(utxo_list, req_amount)
        print('txnout = %s' % bytes.decode(binascii.hexlify(txnout)))
        locktime_b = locktime2bytes(g_locktime)
        sighash_all = binascii.unhexlify('%08x' % 0x01)[::-1]

        preimage_list = []
        sequence = None
        n_inputs = txnin[0:1]
        counter = 0
        for utxo in utxo_list:
                hash160_b = binascii.unhexlify(utxo['hash160'])
                prev_scriptpubkey_b = bytes([0x76, 0xa9, len(hash160_b)]) + hash160_b + bytes([0x88, 0xac])
                prev_scriptpubkey_size_b = bytes([len(prev_scriptpubkey_b)])
                index = (counter * (32 + 4 + 1 + 4)) + 32 + 4 
                inputs = txnin[1:index + 1] + prev_scriptpubkey_size_b + prev_scriptpubkey_b + txnin[index + 2:]
                preimage = version + n_inputs + inputs + txnout + locktime_b + sighash_all
                preimage_list.append(preimage)
                counter += 1
        return preimage_list

#    nVersion:     01000000
#    hashPrevouts: ef546acf4a020de3898d1b8956176bb507e6211b5ed3619cd08b6ea7e2a09d41
#    hashSequence: 0000000000000000000000000000000000000000000000000000000000000000
#    outpoint:     0815cf020f013ed6cf91d29f4202e8a58726b1ac6c79da47c23d1bee0a6925f800000000
#    scriptCode:   (see below)
#    amount:       0011102401000000
#    nSequence:    ffffffff
#    hashOutputs:  0000000000000000000000000000000000000000000000000000000000000000 (this is the second input but there is only one output)
#    nLockTime:    00000000
#    nHashType:    03000000
def get_preimage_list_p2wsh(utxo_list: list, address_pubkeys_map: dict, address_unlock_key_threshold_map: dict):
        global g_locktime
        locktime_b = locktime2bytes(g_locktime)
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        hash_prevouts = get_hash_prevouts(utxo_list)
        hash_sequence = get_hash_sequence(utxo_list)
        hash_outs = get_hash_outs(utxo_list)
        sighash_all = binascii.unhexlify('%08x' % 0x01)[::-1]
        preimage_list = []
        sequence = None
        for utxo in utxo_list:
                outpoint = swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1]
                amount_satoshi = utxo['value']
                amount_b = btc2bytes(amount_satoshi / (10 ** 8))
                witness_program = binascii.unhexlify(utxo['sha256'])
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                redeem_script_b = get_redeem_script_from_pubkey_list(address_pubkeys_map[utxo['address']], address_unlock_key_threshold_map[utxo['address']])
                redeem_script_size_b = bytes([len(redeem_script_b)])
                #redeem_script_size_b = script_utils.encode_pushdata(len(redeem_script_b))
                preimage = version + hash_prevouts + hash_sequence + outpoint + redeem_script_size_b + redeem_script_b + amount_b + sequence + hash_outs + locktime_b + sighash_all
                print('version = %s, hash_prevouts = %s, hash_sequence = %s, outpoint = %s, redeem_script_size = %s, redeem_script = %s, amount = %s, sequence = %s, hash_outs = %s, locktime = %s, sighash_all = %s' % (bytes.decode(binascii.hexlify(version)), bytes.decode(binascii.hexlify(hash_prevouts)), bytes.decode(binascii.hexlify(hash_sequence)), bytes.decode(binascii.hexlify(outpoint)), bytes.decode(binascii.hexlify(redeem_script_size_b)), bytes.decode(binascii.hexlify(redeem_script_b)), bytes.decode(binascii.hexlify(amount_b)), bytes.decode(binascii.hexlify(sequence)), bytes.decode(binascii.hexlify(hash_outs)), bytes.decode(binascii.hexlify(locktime_b)), bytes.decode(binascii.hexlify(sighash_all))))
                preimage_list.append(preimage)
        return preimage_list

#    nVersion:     01000000
#    hashPrevouts: ef546acf4a020de3898d1b8956176bb507e6211b5ed3619cd08b6ea7e2a09d41
#    hashSequence: 0000000000000000000000000000000000000000000000000000000000000000
#    outpoint:     0815cf020f013ed6cf91d29f4202e8a58726b1ac6c79da47c23d1bee0a6925f800000000
#    scriptCode:   (see below)
#    amount:       0011102401000000
#    nSequence:    ffffffff
#    hashOutputs:  0000000000000000000000000000000000000000000000000000000000000000 (this is the second input but there is only one output)
#    nLockTime:    00000000
#    nHashType:    03000000
def get_preimage_list_p2sh_p2wsh(utxo_list: list, address_pubkeys_map: dict, address_unlock_key_threshold_map: dict):
        global g_locktime
        locktime_b = locktime2bytes(g_locktime)
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        hash_prevouts = get_hash_prevouts(utxo_list)
        hash_sequence = get_hash_sequence(utxo_list)
        hash_outs = get_hash_outs(utxo_list)
        sighash_all = binascii.unhexlify('%08x' % 0x01)[::-1]
        preimage_list = []
        sequence = None
        for utxo in utxo_list:
                outpoint = swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1]
                amount_satoshi = utxo['value']
                amount_b = btc2bytes(amount_satoshi / (10 ** 8))
                witness_program = binascii.unhexlify(utxo['hash160'])
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                redeem_script_b = get_redeem_script_from_pubkey_list(address_pubkeys_map[utxo['address']], address_unlock_key_threshold_map[utxo['address']])
                redeem_script_size_b = bytes([len(redeem_script_b)])
                #redeem_script_size_b = script_utils.encode_pushdata(len(redeem_script_b))
                preimage = version + hash_prevouts + hash_sequence + outpoint + redeem_script_size_b + redeem_script_b + amount_b + sequence + hash_outs + locktime_b + sighash_all
                print('version = %s, hash_prevouts = %s, hash_sequence = %s, outpoint = %s, redeem_script_size = %s, redeem_script = %s, amount = %s, sequence = %s, hash_outs = %s, locktime = %s, sighash_all = %s' % (bytes.decode(binascii.hexlify(version)), bytes.decode(binascii.hexlify(hash_prevouts)), bytes.decode(binascii.hexlify(hash_sequence)), bytes.decode(binascii.hexlify(outpoint)), bytes.decode(binascii.hexlify(redeem_script_size_b)), bytes.decode(binascii.hexlify(redeem_script_b)), bytes.decode(binascii.hexlify(amount_b)), bytes.decode(binascii.hexlify(sequence)), bytes.decode(binascii.hexlify(hash_outs)), bytes.decode(binascii.hexlify(locktime_b)), bytes.decode(binascii.hexlify(sighash_all))))
                preimage_list.append(preimage)
        return preimage_list

#    nVersion:     01000000
#    hashPrevouts: 96b827c8483d4e9b96712b6713a7b68d6e8003a781feba36c31143470b4efd37
#    hashSequence: 52b0a642eea2fb7ae638c36f6252b6750293dbe574a806984b8e4d8548339a3b
#    outpoint:     ef51e1b804cc89d182d279655c3aa89e815b1b309fe287d9b2b55d57b90ec68a01000000
#    scriptCode:   1976a9141d0f172a0ecb48aee1be1f2687d2963ae33f71a188ac
#    amount:       0046c32300000000
#    nSequence:    ffffffff
#    hashOutputs:  863ef3e1a92afbfdb97f31ad0fc7683ee943e9abcf2501590ff8f6551f47e5e5
#    nLockTime:    11000000
#    nHashType:    01000000
def get_preimage_list_p2wpkh(utxo_list: list):
        global g_locktime
        locktime_b = locktime2bytes(g_locktime)
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        hash_prevouts = get_hash_prevouts(utxo_list)
        hash_sequence = get_hash_sequence(utxo_list)
        hash_outs = get_hash_outs(utxo_list)
        sighash_all = binascii.unhexlify('%08x' % 0x01)[::-1]
        preimage_list = []
        sequence = None
        for utxo in utxo_list:
                outpoint = swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1]
                amount_satoshi = utxo['value']
                amount_b = btc2bytes(amount_satoshi / (10 ** 8))
                witness_program = binascii.unhexlify(utxo['hash160'])
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                script = bytes([0x76, 0xa9, len(witness_program)]) + witness_program + bytes([0x88, 0xac])
                script_size_b = bytes([len(script)])
                preimage = version + hash_prevouts + hash_sequence + outpoint + script_size_b + script + amount_b + sequence + hash_outs + locktime_b + sighash_all
                print('version = %s, hash_prevouts = %s, hash_sequence = %s, outpoint = %s, script_size = %s, script = %s, amount = %s, sequence = %s, hash_outs = %s, locktime = %s, sighash_all = %s' % (bytes.decode(binascii.hexlify(version)), bytes.decode(binascii.hexlify(hash_prevouts)), bytes.decode(binascii.hexlify(hash_sequence)), bytes.decode(binascii.hexlify(outpoint)), bytes.decode(binascii.hexlify(script_size_b)), bytes.decode(binascii.hexlify(script)), bytes.decode(binascii.hexlify(amount_b)), bytes.decode(binascii.hexlify(sequence)), bytes.decode(binascii.hexlify(hash_outs)), bytes.decode(binascii.hexlify(locktime_b)), bytes.decode(binascii.hexlify(sighash_all))))
                preimage_list.append(preimage)
        return preimage_list

#    nVersion:     01000000
#    hashPrevouts: b0287b4a252ac05af83d2dcef00ba313af78a3e9c329afa216eb3aa2a7b4613a
#    hashSequence: 18606b350cd8bf565266bc352f0caddcf01e8fa789dd8a15386327cf8cabe198
#    outpoint:     db6b1b20aa0fd7b23880be2ecbd4a98130974cf4748fb66092ac4d3ceb1a547701000000
#    scriptCode:   1976a91479091972186c449eb1ded22b78e40d009bdf008988ac
#    amount:       00ca9a3b00000000
#    nSequence:    feffffff
#    hashOutputs:  de984f44532e2173ca0d64314fcefe6d30da6f8cf27bafa706da61df8a226c83
#    nLockTime:    92040000
#    nHashType:    01000000
def get_preimage_list_p2sh_p2wpkh(utxo_list: list, address_script_map: dict):
        global g_locktime
        locktime_b = locktime2bytes(g_locktime)
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        hash_prevouts = get_hash_prevouts(utxo_list)
        hash_sequence = get_hash_sequence(utxo_list)
        hash_outs = get_hash_outs(utxo_list)
        sighash_all = binascii.unhexlify('%08x' % 0x01)[::-1]
        preimage_list = []
        sequence = None
        for utxo in utxo_list:
                outpoint = swap_endian_bytes(binascii.unhexlify(utxo['txn_id'])) + binascii.unhexlify('%08x' % utxo['out_index'])[::-1]
                amount_satoshi = utxo['value']
                amount_b = btc2bytes(amount_satoshi / (10 ** 8))
                witness_program = binascii.unhexlify(utxo['hash160'])
                if sequence == None and g_locktime > 0:
                        sequence = b'\xee\xff\xff\xff'
                else:
                        sequence = b'\xff\xff\xff\xff'
                address_s = pubkey_address.sh2address(binascii.unhexlify(utxo['hash160']), g_nettype)
                hash160_b = binascii.unhexlify(address_script_map[address_s])[2:]
                script = bytes([0x76, 0xa9, len(hash160_b)]) + hash160_b + bytes([0x88, 0xac])
                script_size_b = bytes([len(script)])
                preimage = version + hash_prevouts + hash_sequence + outpoint + script_size_b + script + amount_b + sequence + hash_outs + locktime_b + sighash_all
                print('version = %s, hash_prevouts = %s, hash_sequence = %s, outpoint = %s, script_size = %s, script = %s, amount = %s, sequence = %s, hash_outs = %s, locktime = %s, sighash_all = %s' % (bytes.decode(binascii.hexlify(version)), bytes.decode(binascii.hexlify(hash_prevouts)), bytes.decode(binascii.hexlify(hash_sequence)), bytes.decode(binascii.hexlify(outpoint)), bytes.decode(binascii.hexlify(script_size_b)), bytes.decode(binascii.hexlify(script)), bytes.decode(binascii.hexlify(amount_b)), bytes.decode(binascii.hexlify(sequence)), bytes.decode(binascii.hexlify(hash_outs)), bytes.decode(binascii.hexlify(locktime_b)), bytes.decode(binascii.hexlify(sighash_all))))
                preimage_list.append(preimage)
        return preimage_list

def sign_txn_input(preimage: bytes, privkey_wif: str):
        print('privkey_wif = %s' % privkey_wif)
        hash_preimage = hash_utils.hash256(preimage)
        #privkey_wif = keymap['privkey']
        privkey_s = pubkey_address.privkeyWif2Hex(privkey_wif)
        print('privkey_s = %s' % privkey_s)
        privkey_b = binascii.unhexlify(privkey_s)[:-1]
        signingkey = ecdsa.SigningKey.from_string(privkey_b, curve=ecdsa.SECP256k1)
        sig_b = signingkey.sign_digest(hash_preimage, sigencode=ecdsa.util.sigencode_der_canonize) +b'\x01'
        print('sig = %s' % bytes.decode(binascii.hexlify(sig_b)))
        return sig_b

def prepare_signed_txn_p2wpkh():
        global g_locktime
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        marker = b'\x00'
        segwit_flag = b'\x01'
        keymap_list = get_funding_address_keys_p2wpkh()
        address_list = [keymap['address'] for keymap in keymap_list]
        utxo_list = get_utxos_for_address(address_list, req_amount)
        txn_inputs = prepare_txn_inputs_bare_witness(utxo_list)
        txn_outs = prepare_txn_outs(utxo_list, req_amount)
        preimage_list = get_preimage_list_p2wpkh(utxo_list)
        address_privkey_map = dict(iter([(keymap['address'], keymap['privkey']) for keymap in keymap_list]))
        address_pubkey_map = dict(iter([(keymap['address'], keymap['pubkey']) for keymap in keymap_list]))
        witness_b = b''
        for preimage, utxo in zip(preimage_list, utxo_list):
                print('utxo = %s' % utxo)
                witness_b += bytes([2])
                sig_b = sign_txn_input(preimage, address_privkey_map[utxo['address']])
                witness_b += bytes([len(sig_b)])
                witness_b += sig_b
                pubkey_b = binascii.unhexlify(address_pubkey_map[utxo['address']])
                witness_b += bytes([len(pubkey_b)])
                witness_b += pubkey_b
                print('address = %s, signature = %s, preimage = %s' % (utxo['address'], bytes.decode(binascii.hexlify(sig_b)), bytes.decode(binascii.hexlify(preimage))))
        locktime_b = locktime2bytes(g_locktime)
        print('locktime_b = %s' % bytes.decode(binascii.hexlify(locktime_b)))
        print('preimage_list = %s' % [bytes.decode(binascii.hexlify(preimage)) for preimage in preimage_list])
        signed_txn = version + marker + segwit_flag + txn_inputs + txn_outs + witness_b + locktime_b
        return signed_txn

def prepare_signed_txn_p2sh_p2wpkh():
        global g_locktime
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        marker = b'\x00'
        segwit_flag = b'\x01'
        keymap_list = get_funding_address_keys_p2sh_p2wpkh()
        address_list = [keymap['address'] for keymap in keymap_list]
        utxo_list = get_utxos_for_address(address_list, req_amount)
        address_script_map = dict(iter([(keymap['address'], keymap['script']) for keymap in keymap_list]))
        print('IIIIIIIIIIIIII address_script_map = %s' % address_script_map)
        txn_inputs = prepare_txn_inputs_p2sh_p2wpkh(utxo_list, address_script_map)
        txn_outs = prepare_txn_outs(utxo_list, req_amount)
        preimage_list = get_preimage_list_p2sh_p2wpkh(utxo_list, address_script_map)
        address_privkey_map = dict(iter([(keymap['address'], keymap['privkey']) for keymap in keymap_list]))
        address_pubkey_map = dict(iter([(keymap['address'], keymap['pubkey']) for keymap in keymap_list]))
        witness_b = b''
        for preimage, utxo in zip(preimage_list, utxo_list):
                print('utxo = %s' % utxo)
                witness_b += bytes([2])
                sig_b = sign_txn_input(preimage, address_privkey_map[utxo['address']])
                witness_b += bytes([len(sig_b)])
                witness_b += sig_b
                pubkey_b = binascii.unhexlify(address_pubkey_map[utxo['address']])
                witness_b += bytes([len(pubkey_b)])
                witness_b += pubkey_b
                print('address = %s, signature = %s, preimage = %s' % (utxo['address'], bytes.decode(binascii.hexlify(sig_b)), bytes.decode(binascii.hexlify(preimage))))
        locktime_b = locktime2bytes(g_locktime)
        print('locktime_b = %s' % bytes.decode(binascii.hexlify(locktime_b)))
        print('preimage_list = %s' % [bytes.decode(binascii.hexlify(preimage)) for preimage in preimage_list])
        signed_txn = version + marker + segwit_flag + txn_inputs + txn_outs + witness_b + locktime_b
        return signed_txn

def prepare_signed_txn_p2pkh():
        global g_locktime
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        #marker = b'\x00'
        #segwit_flag = b'\x01'
        keymap_list = get_funding_address_keys_p2pkh()
        address_list = [keymap['address'] for keymap in keymap_list]
        utxo_list = get_utxos_for_address(address_list, req_amount)
        address_privkey_map = dict(iter([(keymap['address'], keymap['privkey']) for keymap in keymap_list]))
        address_pubkey_map = dict(iter([(keymap['address'], keymap['pubkey']) for keymap in keymap_list]))
        preimage_list = get_preimage_list_p2pkh(utxo_list)
        txn_inputs = prepare_txn_inputs_p2pkh(utxo_list, preimage_list, address_privkey_map, address_pubkey_map)
        txn_outs = prepare_txn_outs(utxo_list, req_amount)
        locktime_b = locktime2bytes(g_locktime)
        print('locktime_b = %s' % bytes.decode(binascii.hexlify(locktime_b)))
        print('preimage_list = %s' % [bytes.decode(binascii.hexlify(preimage)) for preimage in preimage_list])
        #signed_txn = version + marker + segwit_flag + txn_inputs + txn_outs + witness_b + locktime_b
        signed_txn = version + txn_inputs + txn_outs + locktime_b
        return signed_txn

def prepare_signed_txn_p2wsh():
        global g_locktime
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        marker = b'\x00'
        segwit_flag = b'\x01'
        keymaplist_list = get_funding_address_keys_p2wsh()
        address_list  = [get_p2wsh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']) for keymaplist in keymaplist_list]
        print('address_list = %s' % address_list)
        utxo_list = get_utxos_for_address(address_list, req_amount)
        txn_inputs = prepare_txn_inputs_bare_witness(utxo_list)
        txn_outs = prepare_txn_outs(utxo_list, req_amount)
        address_pubkeys_map  = dict(iter([(get_p2wsh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']), [keymap['pubkey'] for keymap in keymaplist['Keymap List']]) for keymaplist in keymaplist_list]))
        address_privkeys_map  = dict(iter([(get_p2wsh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']), [keymap['privkey'] for keymap in keymaplist['Keymap List'][0: keymaplist['Unlock Key Threshold']]]) for keymaplist in keymaplist_list]))
        address_unlock_key_threshold_map  = dict(iter([(get_p2wsh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']), keymaplist['Unlock Key Threshold']) for keymaplist in keymaplist_list]))
        preimage_list = get_preimage_list_p2wsh(utxo_list, address_pubkeys_map, address_unlock_key_threshold_map)
        witness_b = b''
        for preimage, utxo in zip(preimage_list, utxo_list):
                print('utxo = %s' % utxo)
                witness_b += bytes([1 + address_unlock_key_threshold_map[utxo['address']] + 1])
                witness_b += b'\x00'
                for privkey_b in address_privkeys_map[utxo['address']]:
                        sig_b = sign_txn_input(preimage, privkey_b)
                        witness_b += bytes([len(sig_b)])
                        witness_b += sig_b
                redeem_script_b = get_redeem_script_from_pubkey_list(address_pubkeys_map[utxo['address']], address_unlock_key_threshold_map[utxo['address']])
                witness_b += bytes([len(redeem_script_b)])
                #witness_b += script_utils.encode_pushdata(len(redeem_script_b))
                witness_b += redeem_script_b
                print('address = %s, signature = %s, preimage = %s' % (utxo['address'], bytes.decode(binascii.hexlify(sig_b)), bytes.decode(binascii.hexlify(preimage))))
        locktime_b = locktime2bytes(g_locktime)
        print('locktime_b = %s' % bytes.decode(binascii.hexlify(locktime_b)))
        print('preimage_list = %s' % [bytes.decode(binascii.hexlify(preimage)) for preimage in preimage_list])
        signed_txn = version + marker + segwit_flag + txn_inputs + txn_outs + witness_b + locktime_b
        return signed_txn

def get_address_redeem_script_map():
        pass

def get_address_pubkey_map():
        pass

def get_address_privkeys_map():
        pass

def get_address_unlock_key_threshold_map():
        pass

supported_scripts = ['P2PKH', 'P2SH-Multisig', 'P2WPKH', 'P2WSH-Multisig', 'P2SH-P2WPKH', 'P2SH-P2WSH-Multisig']

def get_address_key_map_p2pkh(src_info_list: list):
        address_map = {}
        for src_info in src_info_list:
                if 'Access Key' in src_info:
                        # {address_s: {'Public Key': pubkey_s, 'Private Key': privkey_wif, 'Hash 160': h_s}}
                        get_p2pkh_address(src_info['Access Key']))
                        continue
                if 'Address' in src_info:
                        address_map[src_info['Address']] = {'Private Key': src_info['Private Key']}
                        continue
        return address_map

def get_address_key_map_p2sh_multisig(src_info_list: list):
        address_map = {}
        for src_info in src_info_list: list):
                if 'Access Key' in src_info:
                        address_map.update(get_p2sh_address_from_access_keys(src_info['Access Key'], src_info['Unlock Key Threshold']))
                        continue
                if 'Public Keys' in src_info:
                        address_map.update(get_p2sh_address_from_public_keys(src_info['Public Keys'], src_info['Private Keys']))
                        continue

def get_address_key_map():
        address_map = {}
        for source, src_info_list in g_source_info.items():
                if source == 'P2PKH':
                        address_map.update(get_address_key_map_p2pkh(src_info_list))
                        continue
                if source == 'P2SH-Multisig':
                        address_map.update(get_address_key_map_p2sh_multisig(src_info_list))
                        continue
                if source == 'P2WPKH':
                        address_map.update(get_address_key_map_p2wpkh(src_info_list))
                        continue
                if source == 'P2WSH-Multisig':
                        address_map.update(get_address_key_map_p2wsh_multisig(src_info_list))
                        continue
                if source == 'P2SH-P2WPKH':
                        address_map.update(get_address_key_map_p2sh_p2wpkh(src_info_list))
                        continue
                if source == 'P2SH-P2WSH-Multisig':
                        address_map.update(get_address_key_map_p2sh_p2wsh_multisig(src_info_list))
                        continue
        return address_map

def prepare_signed_txn_p2sh_p2wsh():
        global g_locktime
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        marker = b'\x00'
        segwit_flag = b'\x01'
        keymaplist_list = get_funding_address_keys_p2sh_p2wsh()
        address_list  = [get_p2sh_p2wsh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']) for keymaplist in keymaplist_list]
        print('address_list = %s' % address_list)
        utxo_list = get_utxos_for_address(address_list, req_amount)
        #txn_inputs = prepare_txn_inputs_bare_witness(utxo_list)
        txn_outs = prepare_txn_outs(utxo_list, req_amount)
        address_pubkeys_map  = dict(iter([(get_p2sh_p2wsh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']), [keymap['pubkey'] for keymap in keymaplist['Keymap List']]) for keymaplist in keymaplist_list]))
        address_privkeys_map  = dict(iter([(get_p2sh_p2wsh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']), [keymap['privkey'] for keymap in keymaplist['Keymap List'][0: keymaplist['Unlock Key Threshold']]]) for keymaplist in keymaplist_list]))
        address_unlock_key_threshold_map  = dict(iter([(get_p2sh_p2wsh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']), keymaplist['Unlock Key Threshold']) for keymaplist in keymaplist_list]))
        txn_inputs = prepare_txn_inputs_p2sh_p2wsh(utxo_list, address_pubkeys_map, address_unlock_key_threshold_map)
        preimage_list = get_preimage_list_p2sh_p2wsh(utxo_list, address_pubkeys_map, address_unlock_key_threshold_map)
        witness_b = b''
        for preimage, utxo in zip(preimage_list, utxo_list):
                print('utxo = %s' % utxo)
                witness_b += bytes([1 + address_unlock_key_threshold_map[utxo['address']] + 1])
                witness_b += b'\x00'
                for privkey_b in address_privkeys_map[utxo['address']]:
                        sig_b = sign_txn_input(preimage, privkey_b)
                        witness_b += bytes([len(sig_b)])
                        witness_b += sig_b
                redeem_script_b = get_redeem_script_from_pubkey_list(address_pubkeys_map[utxo['address']], address_unlock_key_threshold_map[utxo['address']])
                witness_b += bytes([len(redeem_script_b)])
                #witness_b += script_utils.encode_pushdata(len(redeem_script_b))
                witness_b += redeem_script_b
                print('address = %s, signature = %s, preimage = %s' % (utxo['address'], bytes.decode(binascii.hexlify(sig_b)), bytes.decode(binascii.hexlify(preimage))))
        locktime_b = locktime2bytes(g_locktime)
        print('locktime_b = %s' % bytes.decode(binascii.hexlify(locktime_b)))
        print('preimage_list = %s' % [bytes.decode(binascii.hexlify(preimage)) for preimage in preimage_list])
        signed_txn = version + marker + segwit_flag + txn_inputs + txn_outs + witness_b + locktime_b
        return signed_txn

def prepare_signed_txn_p2sh_multisig():
        global g_locktime
        req_amount = get_required_amount()
        version = binascii.unhexlify('%08x' % 0x02)[::-1]
        #marker = b'\x00'
        #segwit_flag = b'\x01'
        keymaplist_list = get_funding_address_keys_p2sh()
        #address_list = [keymaplist['Keymap List'] for keymaplist in keymaplist_list]
        address_list  = [get_p2sh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']) for keymaplist in keymaplist_list]
        print('address_list = %s' % address_list)
        utxo_list = get_utxos_for_address(address_list, req_amount)
        address_pubkeys_map  = dict(iter([(get_p2sh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']), [keymap['pubkey'] for keymap in keymaplist['Keymap List']]) for keymaplist in keymaplist_list]))
        address_privkeys_map  = dict(iter([(get_p2sh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']), [keymap['privkey'] for keymap in keymaplist['Keymap List']]) for keymaplist in keymaplist_list]))
        address_unlock_key_threshold_map  = dict(iter([(get_p2sh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']), keymaplist['Unlock Key Threshold']) for keymaplist in keymaplist_list]))
        #address_unlock_key_threshold_map = [keymaplist['Unlock Key Threshold'] for keymaplist in keymaplist_list]
        preimage_list = get_preimage_list_p2sh(utxo_list, address_pubkeys_map, address_unlock_key_threshold_map)
        txn_inputs = prepare_txn_inputs_p2sh(utxo_list, preimage_list, address_privkeys_map, address_pubkeys_map, address_unlock_key_threshold_map)
        txn_outs = prepare_txn_outs(utxo_list, req_amount)
        locktime_b = locktime2bytes(g_locktime)
        print('locktime_b = %s' % bytes.decode(binascii.hexlify(locktime_b)))
        print('preimage_list = %s' % [bytes.decode(binascii.hexlify(preimage)) for preimage in preimage_list])
        #signed_txn = version + marker + segwit_flag + txn_inputs + txn_outs + witness_b + locktime_b
        signed_txn = version + txn_inputs + txn_outs + locktime_b
        return signed_txn

def process_transaction():
        raw_txn = prepare_raw_txn()
        pass

if __name__ == '__main__':
        #privkey, pubkey, h160, address = get_p2wpkh_address()
        #print('privkey = %s, pubkey = %s, hash160 = %s, address = %s' % (privkey, pubkey, h160, address))
        #utxos = get_utxos_for_address(address, amount = 125)
        #print('utxos = %s' % utxos)
        #prepare_raw_txn()
        #get_default_locking_script('1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX')
        #get_default_locking_script('bc1qq3q342clxm2p04hfdknhe3cg6mrs8ur8jfln7h')
        #sign_txn_input()
#        signed_txn = prepare_signed_txn_p2wpkh()
#        print('signed_txn = %s' % bytes.decode(binascii.hexlify(signed_txn)))

#        signed_txn = prepare_signed_txn_p2sh_p2wpkh()
#        print('signed_txn = %s' % bytes.decode(binascii.hexlify(signed_txn)))

#        signed_txn = prepare_signed_txn_p2pkh()
#        print('signed_txn = %s' % bytes.decode(binascii.hexlify(signed_txn)))

#        signed_txn = prepare_signed_txn_p2sh()
#        print('signed_txn = %s' % bytes.decode(binascii.hexlify(signed_txn)))

#        signed_txn = prepare_signed_txn_p2wsh()
#        print('signed_txn = %s' % bytes.decode(binascii.hexlify(signed_txn)))

        signed_txn = prepare_signed_txn_p2sh_p2wsh()
        print('signed_txn = %s' % bytes.decode(binascii.hexlify(signed_txn)))

#        privkey = '619c335025c7f4012e556c2a58b2506e30b8511b53ade95ea316fd8c3286feb9'.zfill(64)
#        txhash = 'c37af31116d1b27caf68aae9e3ac82f1477929014d5b917657d0eb49478cb670'.zfill(64)
#        signingkey = ecdsa.SigningKey.from_string(binascii.unhexlify(privkey), curve=ecdsa.SECP256k1)
#        sig_b = signingkey.sign_digest(binascii.unhexlify(txhash), sigencode=ecdsa.util.sigencode_der_canonize) + b'\x01'
#        print('sig = %s' % bytes.decode(binascii.hexlify(sig_b)))
        #vk = ecdsa.VerifyingKey.from_string(pubkey_b, curve=ecdsa.SECP256k1)

        print('amount 6 => in bytes = %s' % bytes.decode(binascii.hexlify(btc2bytes(6))))

#        keymaplist_list = get_funding_address_keys_p2sh_p2wsh()
#        address_list  = [get_p2sh_p2wsh_address_from_pubkey_list([keymap['pubkey'] for keymap in keymaplist['Keymap List']], keymaplist['Unlock Key Threshold']) for keymaplist in keymaplist_list]
#        print('P2Sh-P2WSH address = %s' % address_list)
#        privkey_wif, pubkey_s1, h_s, address_s = get_p2pkh_address('m/7')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s1, h_s, address_s))
#        privkey_wif, pubkey_s2, h_s, address_s = get_p2pkh_address('m/8')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s2, h_s, address_s))
#        privkey_wif, pubkey_s3, h_s, address_s = get_p2pkh_address('m/9')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s3, h_s, address_s))
#        address = get_p2wsh_address_from_pubkey_list([pubkey_s1, pubkey_s2, pubkey_s3], 2)
#        print('P2WSH address = %s' % address)
#        privkey_wif, pubkey_s1, h_s, address_s = get_p2pkh_address('m/7')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s1, h_s, address_s))
#        privkey_wif, pubkey_s2, h_s, address_s = get_p2pkh_address('m/8')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s2, h_s, address_s))
#        privkey_wif, pubkey_s3, h_s, address_s = get_p2pkh_address('m/9')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s3, h_s, address_s))
#        address = get_p2sh_address_from_pubkey_list([pubkey_s1, pubkey_s2, pubkey_s3], 2)
#        print('P2SH address = %s' % address)
#        privkey_wif, pubkey_s, h_s, address_s = get_p2pkh_address('m/0')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s, h_s, address_s))
#        privkey_wif, pubkey_s, h_s, address_s = get_p2sh_p2wpkh_address('m/10')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s, h_s, address_s))
#        privkey_wif, pubkey_s, h_s, address_s = get_p2pkh_address('m/30')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s, h_s, address_s))
#        privkey_wif, pubkey_s, h_s, address_s = get_p2pkh_address('m/1')
#        print('privkey_wif = %s, pubkey_s = %s, h_s = %s, address_s = %s' % (privkey_wif, pubkey_s, h_s, address_s))
