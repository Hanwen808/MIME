module gmii_2_rgmii(
    input              sys_clk,
    input              idelay_clk  , //IDELAY时钟
    input              rst_n,
    //以太网GMII接口
    output             gmii_rx_clk , //GMII接收时钟
    output             gmii_rx_dv  , //GMII接收数据有效信号
    output      [7:0]  gmii_rxd    , //GMII接收数据
    output             gmii_tx_clk , //GMII发送时钟
    input              gmii_tx_en  , //GMII发送数据使能信号
    input       [7:0]  gmii_txd    , //GMII发送数据            
    //以太网RGMII接口   
    input              rgmii_rxc   , //RGMII接收时钟
    input              rgmii_rx_ctl, //RGMII接收数据控制信号
    input       [3:0]  rgmii_rxd   , //RGMII接收数据
    output             rgmii_txc   , //RGMII发送时钟    
    output             rgmii_tx_ctl, //RGMII发送数据控制信号
    output      [3:0]  rgmii_txd   , //RGMII发送数据 
    
    output      rec_pkt_done,
    output      [31:0] src,    
    output      [31:0] dst     
    );

//parameter define
parameter IDELAY_VALUE = 0;  //输入数据IO延时(如果为n,表示延时n*78ps) 

//*****************************************************
//**                    main code
//*****************************************************

assign gmii_tx_clk = gmii_rx_clk;

//RGMII接收
rgmii_rx1 
    #(
     .IDELAY_VALUE  (IDELAY_VALUE)
     )
    u_rgmii_rx1(
    .idelay_clk    (idelay_clk),
    .gmii_rx_clk   (gmii_rx_clk),
    .rgmii_rxc     (rgmii_rxc   ),
    .rgmii_rx_ctl  (rgmii_rx_ctl),
    .rgmii_rxd     (rgmii_rxd   ),
    
    .gmii_rx_dv    (gmii_rx_dv ),
    .gmii_rxd      (gmii_rxd   )
    );

//RGMII发送
rgmii_tx1 u_rgmii_tx1(
    .gmii_tx_clk   (gmii_tx_clk ),
    .gmii_tx_en    (gmii_tx_en  ),
    .gmii_txd      (gmii_txd    ),
              
    .rgmii_txc     (rgmii_txc   ),
    .rgmii_tx_ctl  (rgmii_tx_ctl),
    .rgmii_txd     (rgmii_txd   )
    );

udp_top udp_top_1(
    .sys_clk   (sys_clk),            //外部50M时钟
    .rst_n    (rst_n)   , //复位信号，低电平有效
    //input gmii
    .gmii_rx_clk (gmii_tx_clk), //GMII接收数据时钟
    .gmii_rx_dv  (gmii_tx_en), //GMII输入数据有效信号
    .gmii_rxd    (gmii_txd), //GMII输入数据 
    //output
    .rec_pkt_done   (rec_pkt_done), //以太网单包数据接收完成信号
    .rec_en       ()  , //以太网接收的数据使能信号
    .rec_data     ()  , //以太网接收的数据  
 
    .src       (src)     , 
    .dst     (dst) 
    );




endmodule