module cpu(
    input clk,
    input reset,
    input [3:0] KEY,
    input [9:0] SW,
    output [9:0] LEDR
);

reg [31:0] pc;
reg [31:0] imem [0:255];
reg [31:0] dmem [0:255];

integer j;

reg [9:0] ledr_reg;
assign LEDR = ledr_reg;

//Current instruction
wire [31:0] instr;
//word-aligned instruction fetch
assign instr = imem[pc[9:2]];

// Decode fields
wire [3:0] opcode;
wire [3:0] fn;
wire [15:0] imm;
wire [3:0] rd;
wire [3:0] normal_rs1;
wire [3:0] normal_rs2;

assign opcode = instr[3:0];
assign fn = instr[7:4];
assign imm = instr[23:8];
assign normal_rs2 = instr[23:20];
assign normal_rs1 = instr[27:24];
assign rd = instr[31:28];

//Sign-extended immediate
wire [31:0] imm_sext;
assign imm_sext = {{16{imm[15]}}, imm};

wire branch_or_store;
assign branch_or_store = (opcode == 4'h6 || opcode == 4'h5);

wire [3:0] read_rs1;
wire [3:0] read_rs2;

assign read_rs1 = branch_or_store ? instr[31:28] : normal_rs1;
assign read_rs2 = branch_or_store ? instr[27:24] : normal_rs2;

// Register file wires
wire [31:0] rs1_val;
wire [31:0] rs2_val;

reg write_enable;
reg [31:0] write_data;

regfile rf0(
    .clk(clk),
    .reset(reset),

    .rs1(read_rs1),
    .rs2(read_rs2),
    .rd(rd),

    .write_enable(write_enable),
    .write_data(write_data),

    .rs1_val(rs1_val),
    .rs2_val(rs2_val)
);

//LW/SW
wire [31:0] addr;
wire [7:0] dmem_index;

assign addr = rs1_val + imm_sext;
assign dmem_index = addr[9:2];

//ALU
wire [31:0] alu_b;
wire [31:0] alu_result;

assign alu_b = (opcode == 4'h8) ? imm_sext : rs2_val;

alu alu0(
    .a(rs1_val),
    .b(alu_b),
    .fn(fn),
    .result(alu_result)
);

//CMP
wire [31:0] cmp_b;
wire [31:0] cmp_result;

assign cmp_b = (opcode == 4'hA) ? imm_sext : rs2_val;

cmp cmp0(
    .a(rs1_val),
    .b(cmp_b),
    .fn(fn),
    .result(cmp_result)
);

//Branch/PC control
wire branch_taken;
reg [31:0] next_pc;

branch branch0(
    .a(rs1_val),
    .b(rs2_val),
    .fn(fn),
    .taken(branch_taken)
);

//Initialize memory
initial begin
    for (j = 0; j < 256; j = j + 1) begin
        imem[j] = 32'h00000000;
        dmem[j] = 32'h00000000;
    end

    ledr_reg = 10'b0;

    //Load assembler output here
    //$readmemh("program.mem", imem);
end

//Combinational control logic
always @(*) begin
    write_enable = 0;
    write_data = 32'd0;
    next_pc = pc + 4;

    case (opcode)

        4'h0: begin
            //ALUR
            write_enable = 1;
            write_data = alu_result;
        end

        4'h8: begin
            //ALUI and MVHI
            write_enable = 1;

            if (fn == 4'hB) begin
                write_data = {imm, 16'b0}; // MVHI
            end else begin
                write_data = alu_result;
            end
        end

        4'h2: begin
            //CMPR
            write_enable = 1;
            write_data = cmp_result;
        end

        4'hA: begin
            //CMPI
            write_enable = 1;
            write_data = cmp_result;
        end

        4'h4: begin
            //LW
            write_enable = 1;

            if (addr == 32'hF0000010) begin
                write_data = {28'd0, KEY};
            end else if (addr == 32'hF0000014) begin
                write_data = {22'd0, SW};
            end else begin
                write_data = dmem[dmem_index];
            end
        end
        4'h6: begin
            if (branch_taken) begin
                next_pc = pc + 4 + (imm_sext << 2);
            end
        end

        4'hB: begin
            // JAL
            if (fn == 4'h0) begin
                write_enable = 1;
                write_data = pc + 4;
                next_pc = rs1_val + (imm_sext << 2);
            end
        end

        default: begin
            // do nothing
        end

    endcase
end
always @(posedge clk) begin
    if (reset) begin
        pc <= 32'h40;
        ledr_reg <= 10'b0;
    end else begin
        //SW
        if (opcode == 4'h5) begin
            if (addr == 32'hF0000004) begin
                ledr_reg <= rs2_val[9:0];
            end else begin
                dmem[dmem_index] <= rs2_val;
            end
        end
        pc <= next_pc;
        $display("PC=%h instr=%h op=%h fn=%h rd=R%0d rs1=R%0d(%0d) rs2=R%0d(%0d) imm=%h write=%b wdata=%0d LEDR=%b",
            pc, instr, opcode, fn, rd, read_rs1, rs1_val, read_rs2, rs2_val,
            imm, write_enable, write_data, LEDR);
    end
end

endmodule