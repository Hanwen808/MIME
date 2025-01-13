module udp_top(
    input              sys_clk,
    input                rst_n       , //复位信号，低电平有效
    //GMII接口
    input                gmii_rx_clk , //GMII接收数据时钟
    input                gmii_rx_dv  , //GMII输入数据有效信号
    input        [7:0]   gmii_rxd    , //GMII输入数据

    //用户接口
    output               rec_pkt_done, //以太网单包数据接收完成信号
    output               rec_en      , //以太网接收的数据使能信号
    output       [31:0]  rec_data    , //以太网接收的数据
     
    output       [31:0]  src         , 
    output       [31:0]  dst   
    );


//*****************************************************
//**                    main code
//*****************************************************

//以太网接收模块    
udp_rx 
   u_udp_rx(
    .sys_clk   (sys_clk),            //外部50M时钟
    .clk             (gmii_rx_clk ),        
    .rst_n           (rst_n       ),             
    .gmii_rx_dv      (gmii_rx_dv  ),                                 
    .gmii_rxd        (gmii_rxd    ),       
    .rec_pkt_done    (rec_pkt_done),      
    .rec_en          (rec_en      ),            
    .rec_data        (rec_data    ),
    .des_ip             (dst         ),
    .src             (src         ),          
    .rec_byte_num    ()       
    );                                    



endmodule