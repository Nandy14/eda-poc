module bit_parity (D, Pin, Pout);

input D, Pin;
output Pout;

wire Pout;


XOR2SGD0BWP30P140 G1(.A1(D), .A2(Pin), .Z(Pout)); // nibble_parit

endmodule

module nibble_parity (D, EN, DP);
 
input [3:0] D, EN;
output [4:0] DP;

wire n1, n2, n3, n4, n5, n6, n7, n8;

bit_parity          p0   (.D(D[0]), .Pin (1'b0), .Pout (n1));
CKMUX2SGD1BWP30P140 mux0 (.I0(1'b0), .I1(n1), .S(EN[0]), .Z(n2));
bit_parity          p1   (.D(D[1]),  .Pin (n2),  .Pout (n3));
CKMUX2SGD1BWP30P140 mux1 (.I0(n2), .I1(n3), .S(EN[1]), .Z(n4));
bit_parity          p2   (.D(D[2]),  .Pin (n4),  .Pout (n5));
CKMUX2SGD1BWP30P140 mux2 (.I0(n4), .I1(n5), .S(EN[2]), .Z(n6));
bit_parity          p3   (.D(D[3]),  .Pin (n6),  .Pout (n7));
CKMUX2SGD1BWP30P140 mux3 (.I0(n6), .I1(n7), .S(EN[3]), .Z(DP[4]));
BUFFSGD3BWP30P140HVT buf0 (.I(D[0]), .Z(DP[0]));
BUFFSGD3BWP30P140HVT buf1 (.I(D[1]), .Z(DP[1]));
BUFFSGD3BWP30P140HVT buf2 (.I(D[2]), .Z(DP[2]));
BUFFSGD3BWP30P140HVT buf3 (.I(D[3]), .Z(DP[3]));

endmodule





