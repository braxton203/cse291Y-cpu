`timescale 1ns/1ps

module cpu_tb;

reg clk;
reg reset;
reg [3:0] KEY;
reg [9:0] SW;
wire [9:0] LEDR;

cpu uut (
    .clk(clk),
    .reset(reset),
    .KEY(KEY),
    .SW(SW),
    .LEDR(LEDR)
);

always #5 clk = ~clk;

initial begin
    clk = 0;
    reset = 1;
    KEY = 0;
    SW = 0;

    #10;
    reset = 0;

    #370;
    $finish;
end

endmodule