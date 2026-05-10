module regfile(
    input clk,
    input reset,

    input [3:0] rs1,
    input [3:0] rs2,
    input [3:0] rd,

    input write_enable,
    input [31:0] write_data,

    output [31:0] rs1_val,
    output [31:0] rs2_val
);

reg [31:0] regs [0:15];
integer i;

assign rs1_val = regs[rs1];
assign rs2_val = regs[rs2];

always @(posedge clk) begin
    if (reset) begin
        for (i = 0; i < 16; i = i + 1) begin
            regs[i] <= 32'd0;
        end
    end else if (write_enable) begin
        regs[rd] <= write_data;
    end
end

endmodule