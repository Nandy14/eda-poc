module counter ( clk, reset, enable, dat_out );
  output [15:0] dat_out;
  input clk, reset, enable;
  wire   N69, N70, N71, N72, N73, N74, N75, N76, N77, N78, N79, N80, N81, N82,N83, N84, N86, N88, N90, N92, N94, N96, n42, n43, n44, n45, n46, n47,n48, n49, n50, n51, n52, n53, n54, n55, n56, n57, n58, n59, n60, n61,n62, n63, n64, n65, n66, n67;
 
  EDFFX2AD \dat_out_sig_reg[0]  ( .D(N69), .E(N96), .CK(clk), .Q(dat_out[0])
         );
  EDFFX2AD \dat_out_sig_reg[1]  ( .D(N70), .E(N94), .CK(clk), .Q(dat_out[1])
         );
  EDFFX2AD \dat_out_sig_reg[2]  ( .D(N71), .E(N92), .CK(clk), .Q(dat_out[2])
         );
  EDFFX2AD \dat_out_sig_reg[3]  ( .D(N72), .E(N90), .CK(clk), .Q(dat_out[3])
         );
  EDFFX2AD \dat_out_sig_reg[4]  ( .D(N73), .E(N88), .CK(clk), .Q(dat_out[4])
         );
  EDFFX2AD \dat_out_sig_reg[5]  ( .D(N74), .E(N86), .CK(clk), .Q(dat_out[5])
         );
  DFFQXLAD \dat_out_sig_reg[8]  ( .D(N77), .CK(clk), .Q(dat_out[8]) );
  DFFQXLAD \dat_out_sig_reg[15]  ( .D(N84), .CK(clk), .Q(dat_out[15]) );
  DFFQXLAD \dat_out_sig_reg[6]  ( .D(N75), .CK(clk), .Q(dat_out[6]) );
  DFFQXLAD \dat_out_sig_reg[11]  ( .D(N80), .CK(clk), .Q(dat_out[11]) );
  DFFQXLAD \dat_out_sig_reg[9]  ( .D(N78), .CK(clk), .Q(dat_out[9]) );
  DFFQXLAD \dat_out_sig_reg[13]  ( .D(N82), .CK(clk), .Q(dat_out[13]) );
  DFFQXLAD \dat_out_sig_reg[14]  ( .D(N83), .CK(clk), .Q(dat_out[14]) );
  DFFQXLAD \dat_out_sig_reg[7]  ( .D(N76), .CK(clk), .Q(dat_out[7]) );
  DFFQXLAD \dat_out_sig_reg[10]  ( .D(N79), .CK(clk), .Q(dat_out[10]) );
  DFFQXLAD \dat_out_sig_reg[12]  ( .D(N81), .CK(clk), .Q(dat_out[12]) );
  NAND2BX1AD U53 ( .AN(enable), .B(reset), .Y(N96) );
  OAI2BB1X1AD U54 ( .A0N(dat_out[0]), .A1N(enable), .B0(reset), .Y(N94) );
  INVX1AD U55 ( .A(n42), .Y(N92) );
  AOI31X1AD U56 ( .A0(dat_out[1]), .A1(dat_out[0]), .A2(enable), .B0(n43), .Y(
        n42) );
  NAND2X1AD U57 ( .A(reset), .B(n44), .Y(N90) );
  OAI2BB1X1AD U58 ( .A0N(n45), .A1N(dat_out[3]), .B0(reset), .Y(N88) );
  NAND2X1AD U59 ( .A(reset), .B(n46), .Y(N86) );
  NOR2X1AD U60 ( .A(n47), .B(n43), .Y(N84) );
  XOR2X1AD U61 ( .A(n48), .B(dat_out[15]), .Y(n47) );
  NAND2BX1AD U62 ( .AN(n49), .B(dat_out[14]), .Y(n48) );
  NOR2X1AD U63 ( .A(n50), .B(n43), .Y(N83) );
  XOR2X1AD U64 ( .A(n49), .B(dat_out[14]), .Y(n50) );
  NAND3X1AD U65 ( .A(dat_out[12]), .B(n51), .C(dat_out[13]), .Y(n49) );
  NOR2X1AD U66 ( .A(n52), .B(n43), .Y(N82) );
  XOR2X1AD U67 ( .A(n53), .B(dat_out[13]), .Y(n52) );
  NAND2X1AD U68 ( .A(dat_out[12]), .B(n51), .Y(n53) );
  NOR2X1AD U69 ( .A(n54), .B(n43), .Y(N81) );
  XNOR2X1AD U70 ( .A(dat_out[12]), .B(n51), .Y(n54) );
  NOR2BX1AD U71 ( .AN(dat_out[11]), .B(n55), .Y(n51) );
  NOR2X1AD U72 ( .A(n56), .B(n43), .Y(N80) );
  XOR2X1AD U73 ( .A(n55), .B(dat_out[11]), .Y(n56) );
  NAND2X1AD U74 ( .A(dat_out[10]), .B(n57), .Y(n55) );
  NOR2X1AD U75 ( .A(n58), .B(n43), .Y(N79) );
  XNOR2X1AD U76 ( .A(dat_out[10]), .B(n57), .Y(n58) );
  NOR3BX1AD U77 ( .AN(dat_out[9]), .B(n59), .C(n60), .Y(n57) );
  NOR2X1AD U78 ( .A(n61), .B(n43), .Y(N78) );
  XNOR2X1AD U79 ( .A(dat_out[9]), .B(n62), .Y(n61) );
  NOR2X1AD U80 ( .A(n60), .B(n59), .Y(n62) );
  NOR2X1AD U81 ( .A(n63), .B(n43), .Y(N77) );
  XNOR2X1AD U82 ( .A(n60), .B(n59), .Y(n63) );
  INVX1AD U83 ( .A(dat_out[8]), .Y(n59) );
  NAND2X1AD U84 ( .A(dat_out[7]), .B(n64), .Y(n60) );
  NOR2X1AD U85 ( .A(n65), .B(n43), .Y(N76) );
  XNOR2X1AD U86 ( .A(dat_out[7]), .B(n64), .Y(n65) );
  AND2X1AD U87 ( .A(dat_out[6]), .B(n66), .Y(n64) );
  NOR2X1AD U88 ( .A(n67), .B(n43), .Y(N75) );
  XNOR2X1AD U89 ( .A(n66), .B(dat_out[6]), .Y(n67) );
  NOR2BX1AD U90 ( .AN(dat_out[5]), .B(n46), .Y(n66) );
  NAND3X1AD U91 ( .A(dat_out[3]), .B(n45), .C(dat_out[4]), .Y(n46) );
  INVX1AD U92 ( .A(n44), .Y(n45) );
  NAND4X1AD U93 ( .A(dat_out[2]), .B(dat_out[1]), .C(enable), .D(dat_out[0]),
        .Y(n44) );
  NOR2X1AD U94 ( .A(dat_out[5]), .B(n43), .Y(N74) );
  NOR2X1AD U95 ( .A(dat_out[4]), .B(n43), .Y(N73) );
  NOR2X1AD U96 ( .A(dat_out[3]), .B(n43), .Y(N72) );
  NOR2X1AD U97 ( .A(dat_out[2]), .B(n43), .Y(N71) );
  NOR2X1AD U98 ( .A(dat_out[1]), .B(n43), .Y(N70) );
  NOR2X1AD U99 ( .A(dat_out[0]), .B(n43), .Y(N69) );
  INVX1AD U100 ( .A(reset), .Y(n43) );
endmodule

