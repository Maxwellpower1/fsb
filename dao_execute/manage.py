#!/usr/bin/env python

import os
import sys
import optparse


def run_rpc():
    from dao_execute.rpc import rpc_server
    rpc_server.run()


def run_ctp():
    from dao_execute.exchange_api.ctp import trade_ctps
    trade_ctps.run()


def run_mctp():
    from dao_execute.exchange_api.ctp import trade_ctps
    trade_ctps.monitor_trade_ctps()


def orders():
    from dao_execute.orders import update_orders
    update_orders.main()


def print_info():
    filename = os.path.basename(__file__)
    print('need set param, such as:')
    print('python {} -t rpc'.format(filename))
    print('python {} -t ctp'.format(filename))
    print('python {} -t mctp'.format(filename))
    print('python {} -t orders'.format(filename))


def main():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--type", dest="run_type",
                      help="run_rpc")
    (options, args) = parser.parse_args()
    if options.run_type != None:
        param = options.run_type
        if (param == 'rpc'):
            run_rpc()
        elif (param == 'ctp'):
            run_ctp()
        elif (param == 'mctp'):
            run_mctp()
        elif (param == 'orders'):
            orders()
        else:
            print_info()
            sys.exit(0)
    else:
        print_info()
        sys.exit(0)


if __name__ == '__main__':
    main()
