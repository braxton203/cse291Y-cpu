`timescale 1ns/1ps

module system_tb;

reg clk;
reg reset;

reg [3:0] KEY;
reg [9:0] SW;

wire [9:0] LEDR;

cpu uut(
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

    KEY = 4'b0000;
    SW  = 10'b0000000000;

    #10;
    reset = 0;

    // let assembled program run
    #200;

    $display("FINAL REGS:");
    $display("R1=%0d", uut.rf0.regs[1]);
    $display("R2=%0d", uut.rf0.regs[2]);
    $display("R3=%0d", uut.rf0.regs[3]);
    $display("LEDR=%b", LEDR);

    $finish;
end

endmodule
