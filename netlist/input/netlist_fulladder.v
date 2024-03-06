module fulladdder (A,B,C,Sum,Carry,Clock, Scan_clk,Scan_en,cg_en, gen_clk_mux );
input A,B,C,Clock,Scan_clk,Scan_en,cg_en, gen_clk_mux;
output Sum,Carry;
//wire n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11, n12, n13;
wire  n4, n5, n6, n7, n8, n9, n10, n11, n12, n13, n14, n15, CLK, mux_clock,gated_clock;

//clock Path - Clock - > CLK
CKMUX2SGD1BWP30P140 mux1(.I0(Clock), .I1(Scan_clk), .S(Scan_en), .Z(mux_clock));
AN2SGD0BWP30P140 gate(.A1(mux_clock), .A2(cg_en), .Z(gated_clock));
//LATQ_X1M_A9G33 icg_latch(.G(Clock), .D(gated), .Q(gated_clock));
//Generated clock

BUFFSGD3BWP30P140HVT CLKx_B1 (.I(gated_clock), .Z(CLK) );

SDFQOPPSBSGD1BWP30P140HVT reg1(.D(A), .CP(CLK), .Q(n4), .SI(1'b0), .SE(1'b0));
SDFQOPPSBSGD1BWP30P140HVT reg2(.D(B), .CP(CLK), .Q(n5), .SI(1'b0), .SE(1'b0));
SDFQOPPSBSGD1BWP30P140HVT reg3(.D(C), .CP(CLK), .Q(n6), .SI(1'b0), .SE(1'b0));
XOR2SGD0BWP30P140 G1(.A1(n4), .A2(n5), .Z(n7));
XOR2SGD0BWP30P140 G2(.A1(n7), .A2(n6), .Z(n8));
//BC
AN2SGD0BWP30P140 G3(.A1(n5), .A2(n6), .Z(n9));
//AB
AN2SGD0BWP30P140 G4(.A1(n4), .A2(n5), .Z(n10));
//AC 
AN2SGD0BWP30P140 G5(.A1(n4), .A2(n6), .Z(n11));

OR2SGD1BWP30P140 G7(.A1(n9), .A2(n10), .Z(n12));
OR2SGD1BWP30P140 G6(.A1(n12), .A2(n11), .Z(n13));

SDFQOPPSBSGD1BWP30P140HVT reg4(.D(n13), .CP(CLK), .Q(n14), .SI(1'b0), .SE(1'b0));
SDFQOPPSBSGD1BWP30P140HVT reg5(.D(n8), .CP(CLK), .Q(n15), .SI(1'b0), .SE(1'b0));

BUFFSGD3BWP30P140HVT B1 (.I(n14), .Z(Carry) );
BUFFSGD3BWP30P140HVT B2 (.I(n15), .Z(Sum) );

//get_lib_cells */*BUF*
//get_lib_pins tcbn22ullbwp30p140sgssg0p72vm40c_ccs/BUFFSGD3BWP30P140HVT/*

endmodule



