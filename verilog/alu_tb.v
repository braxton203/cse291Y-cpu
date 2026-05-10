`timescale 1ns/1ps

module alu_tb;

reg [31:0] a;
reg [31:0] b;
reg [3:0] fn;
wire [31:0] result;

alu uut (
    .a(a),
    .b(b),
    .fn(fn),
    .result(result)
);

initial begin
    a = 10;
    b = 4;

    fn = 4'h0; #1; $display("ADD  result=%0d expected=14", result);
    fn = 4'h1; #1; $display("SUB  result=%0d expected=6", result);
    fn = 4'h4; #1; $display("AND  result=%0d expected=0", result);
    fn = 4'h5; #1; $display("OR   result=%0d expected=14", result);
    fn = 4'h6; #1; $display("XOR  result=%0d expected=14", result);
    fn = 4'hC; #1; $display("NAND result=%0d expected=4294967295", result);
    fn = 4'hD; #1; $display("NOR  result=%0d expected=4294967281", result);
    fn = 4'hE; #1; $display("XNOR result=%0d expected=4294967281", result);

    $finish;
end

endmodule
