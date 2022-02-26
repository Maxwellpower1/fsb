service TradeCtp {
    string execute_order(
        1:string user_id,
        2:string exchange,
        3:string account_type,
        4:string strategy_name,
        5:string symbol,
        6:string order_type,
        7:string price,
        8:string amount,
        9:string money_num,
        10:string exec_ts,
        11:string strategy_instance_id,
        12:bool close_today
    );
    string cancel_order(
        1:string user_id,
        2:string exchange,
        3:string account_type,
        4:string strategy_name,
        5:string symbol,
        6:string order_id
    )
}
