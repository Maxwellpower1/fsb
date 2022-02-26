service DaoExecute {
    string execute_order(
        1:string sig,
        2:string user_id,
        3:string exchange,
        4:string account_type,
        5:string strategy_name,
        6:string symbol,
        7:string order_type,
        8:string price,
        9:string amount,
        10:string money_num,
        11:string exec_ts,
        12:string strategy_instance_id,
        13:bool close_today
    );
    string fetch_orders(
        1:string sig,
        2:string user_id,
        3:string exchange,
        4:string account_type,
        5:string strategy_name,
        6:string symbol,
        7:string order_id
    );
    string get_orders(
        1:string sig,
        2:string user_id,
        3:string exchange,
        4:string account_type,
        5:string strategy_name,
        6:string symbol,
        7:string order_status,
        8:string page_num,
        9:string page_limit
    );
    string get_strategy_orders(
        1:string sig,
        2:string user_id,
        3:string strategy_instance_id,
        4:string order_status,
        8:string page_num,
        9:string page_limit
    );
    string cancel_order(
        1:string sig,
        2:string user_id,
        3:string exchange,
        4:string account_type,
        5:string strategy_name,
        6:string symbol,
        7:string order_id
    )
}
