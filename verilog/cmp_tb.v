`timescale 1ns/1ps

module cmp_tb;

reg [31:0] a;
reg [31:0] b;
reg [3:0] fn;
wire [31:0] result;

cmp uut (
    .a(a),
    .b(b),
    .fn(fn),
    .result(result)
);

initial begin
    a = 10;
    b = 4;

    fn = 4'h0; #1; $display("F   result=%0d expected=0", result);
    fn = 4'h1; #1; $display("EQ  result=%0d expected=0", result);
    fn = 4'h2; #1; $display("LT  result=%0d expected=0", result);
    fn = 4'h3; #1; $display("LTE result=%0d expected=0", result);
    fn = 4'h8; #1; $display("T   result=%0d expected=1", result);
    fn = 4'h9; #1; $display("NE  result=%0d expected=1", result);
    fn = 4'hA; #1; $display("GTE result=%0d expected=1", result);
    fn = 4'hB; #1; $display("GT  result=%0d expected=1", result);

    $finish;
end

endmodule
