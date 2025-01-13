module gmii_2_rgmii(
    input              sys_clk,
    input              idelay_clk  , //IDELAYʱ��
    input              rst_n,
    //��̫��GMII�ӿ�
    output             gmii_rx_clk , //GMII����ʱ��
    output             gmii_rx_dv  , //GMII����������Ч�ź�
    output      [7:0]  gmii_rxd    , //GMII��������
    output             gmii_tx_clk , //GMII����ʱ��
    input              gmii_tx_en  , //GMII��������ʹ���ź�
    input       [7:0]  gmii_txd    , //GMII��������            
    //��̫��RGMII�ӿ�   
    input              rgmii_rxc   , //RGMII����ʱ��
    input              rgmii_rx_ctl, //RGMII�������ݿ����ź�
    input       [3:0]  rgmii_rxd   , //RGMII��������
    output             rgmii_txc   , //RGMII����ʱ��    
    output             rgmii_tx_ctl, //RGMII�������ݿ����ź�
    output      [3:0]  rgmii_txd   , //RGMII�������� 
    
    output      rec_pkt_done,
    output      [31:0] src,    
    output      [31:0] dst     
    );

//parameter define
parameter IDELAY_VALUE = 0;  //��������IO��ʱ(���Ϊn,��ʾ��ʱn*78ps) 

//*****************************************************
//**                    main code
//*****************************************************

assign gmii_tx_clk = gmii_rx_clk;

//RGMII����
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

//RGMII����
rgmii_tx1 u_rgmii_tx1(
    .gmii_tx_clk   (gmii_tx_clk ),
    .gmii_tx_en    (gmii_tx_en  ),
    .gmii_txd      (gmii_txd    ),
              
    .rgmii_txc     (rgmii_txc   ),
    .rgmii_tx_ctl  (rgmii_tx_ctl),
    .rgmii_txd     (rgmii_txd   )
    );

udp_top udp_top_1(
    .sys_clk   (sys_clk),            //�ⲿ50Mʱ��
    .rst_n    (rst_n)   , //��λ�źţ��͵�ƽ��Ч
    //input gmii
    .gmii_rx_clk (gmii_tx_clk), //GMII��������ʱ��
    .gmii_rx_dv  (gmii_tx_en), //GMII����������Ч�ź�
    .gmii_rxd    (gmii_txd), //GMII�������� 
    //output
    .rec_pkt_done   (rec_pkt_done), //��̫���������ݽ�������ź�
    .rec_en       ()  , //��̫�����յ�����ʹ���ź�
    .rec_data     ()  , //��̫�����յ�����  
 
    .src       (src)     , 
    .dst     (dst) 
    );




endmodule