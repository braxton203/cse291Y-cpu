`timescale 1ns/1ps

module cpu_jal_tb;

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

    KEY = 0;
    SW = 0;

    // JAL R1, R2, +1
    // ADDI R3,R0,111   (should be skipped)
    // ADDI R4,R0,222   (target)

    uut.imem[16] = 32'h1200020B; // JAL R1,R2,+1
    uut.imem[17] = 32'h30006F08; // ADDI R3,R0,111
    uut.imem[18] = 32'h4000DE08; // ADDI R4,R0,222

    #10;
    reset = 0;

    // preload base register AFTER reset
    uut.rf0.regs[2] = 32'h40; // base PC

    #50;

    $display("R1(link) = %0d expected=68", uut.rf0.regs[1]);
    $display("R3(skip) = %0d expected=0", uut.rf0.regs[3]);
    $display("R4(target)= %0d expected=222", uut.rf0.regs[4]);

    $finish;
end

endmodule
