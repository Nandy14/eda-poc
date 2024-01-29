module fulladdder (
    input  A,
    input  B,
    input  C,
    input  Clock,
    input  Scan_clk,
    input  Scan_en,
    input  cg_en,
    input  gen_clk_mux,
    output  Sum,
    output  Carry
);

    wire  n4;
    wire  n5;
    wire  n6;
    wire  n7;
    wire  n8;
    wire  n9;
    wire  n10;
    wire  n11;
    wire  n12;
    wire  n13;
    wire  n14;
    wire  n15;
    wire  CLK;
    wire  mux_clock;
    wire  gated_clock;
    CKMUX2SGD1BWP30P140 mux1 (.I0(Clock), .I1(Scan_clk), .S(Scan_en), .Z(mux_clock));
    AN2SGD0BWP30P140 gate (.A1(mux_clock), .A2(cg_en), .Z(gated_clock));
    BUFFSGD3BWP30P140HVT CLK_B1 (.I(gated_clock), .Z(CLK));
    SDFQOPPSBSGD1BWP30P140HVT reg1 (.D(A), .CP(CLK), .Q(n4), .SI(1'b0), .SE(1'b0));
    SDFQOPPSBSGD1BWP30P140HVT reg2 (.D(B), .CP(CLK), .Q(n5), .SI(1'b0), .SE(1'b0));
    SDFQOPPSBSGD1BWP30P140HVT reg3 (.D(C), .CP(CLK), .Q(n6), .SI(1'b0), .SE(1'b0));
    XOR2SGD0BWP30P140 G1 (.A1(n4), .A2(n5), .Z(n7));
    XOR2SGD0BWP30P140 G2 (.A1(n7), .A2(n6), .Z(n8));
    AN2SGD0BWP30P140 G3 (.A1(n5), .A2(n6), .Z(n9));
    AN2SGD0BWP30P140 G4 (.A1(n4), .A2(n5), .Z(n10));
    AN2SGD0BWP30P140 G5 (.A1(n4), .A2(n6), .Z(n11));
    OR2SGD1BWP30P140 G7 (.A1(n9), .A2(n10), .Z(n12));
    OR2SGD1BWP30P140 G6 (.A1(n12), .A2(n11), .Z(n13));
    SDFQOPPSBSGD1BWP30P140HVT reg4 (.D(n13), .CP(CLK), .Q(n14), .SI(1'b0), .SE(1'b0));
    SDFQOPPSBSGD1BWP30P140HVT reg5 (.D(n8), .CP(CLK), .Q(n15), .SI(1'b0), .SE(1'b0));
    BUFFSGD3BWP30P140HVT B1 (.I(n14), .Z(Carry));
    BUFFSGD3BWP30P140HVT B2 (.I(n15), .Z(Sum));
endmodule

