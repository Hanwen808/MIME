module udp_top(
    input              sys_clk,
    input                rst_n       , //��λ�źţ��͵�ƽ��Ч
    //GMII�ӿ�
    input                gmii_rx_clk , //GMII��������ʱ��
    input                gmii_rx_dv  , //GMII����������Ч�ź�
    input        [7:0]   gmii_rxd    , //GMII��������

    //�û��ӿ�
    output               rec_pkt_done, //��̫���������ݽ�������ź�
    output               rec_en      , //��̫�����յ�����ʹ���ź�
    output       [31:0]  rec_data    , //��̫�����յ�����
     
    output       [31:0]  src         , 
    output       [31:0]  dst   
    );


//*****************************************************
//**                    main code
//*****************************************************

//��̫������ģ��    
udp_rx 
   u_udp_rx(
    .sys_clk   (sys_clk),            //�ⲿ50Mʱ��
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