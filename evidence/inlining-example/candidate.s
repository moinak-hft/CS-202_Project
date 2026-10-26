	.file	"candidate.c"
	.text
.Ltext0:
	.cfi_sections	.debug_frame
	.file 0 "C:/Users/MOINAK/Documents/Codex/2026-10-25/in-x20/outputs/CS-202_Project-main/.optilab/runs/81cf30fbd418459e98180219060b1f51" "C:/Users/MOINAK/Documents/Codex/2026-10-25/in-x20/outputs/CS-202_Project-main/.optilab/runs/81cf30fbd418459e98180219060b1f51/candidate.c"
	.section .rdata,"dr"
.LC4:
	.ascii "%u\12\0"
	.section	.text.startup,"x"
	.p2align 4
	.globl	main
	.def	main;	.scl	2;	.type	32;	.endef
	.seh_proc	main
main:
.LVL0:
.LFB18:
	.file 1 "C:/Users/MOINAK/Documents/Codex/2026-10-25/in-x20/outputs/CS-202_Project-main/.optilab/runs/81cf30fbd418459e98180219060b1f51/candidate.c"
	.loc 1 15 1 view -0
	.cfi_startproc
	.loc 1 15 1 is_stmt 0 view .LVU1
	pushq	%rsi
	.seh_pushreg	%rsi
	.cfi_def_cfa_offset 16
	.cfi_offset 4, -16
	movl	$65576, %eax
	pushq	%rbx
	.seh_pushreg	%rbx
	.cfi_def_cfa_offset 24
	.cfi_offset 3, -24
	call	___chkstk_ms
	subq	%rax, %rsp
	.seh_stackalloc	65576
	.cfi_def_cfa_offset 65600
	.seh_endprologue
	.loc 1 15 1 view .LVU2
	movl	%ecx, %esi
	movq	%rdx, %rbx
	call	__main
.LVL1:
	.loc 1 16 5 is_stmt 1 view .LVU3
	.loc 1 17 5 view .LVU4
	.loc 1 17 18 is_stmt 0 discriminator 2 view .LVU5
	movl	$400, %r9d
	.loc 1 17 76 view .LVU6
	cmpl	$1, %esi
	jg	.L31
.L2:
.LVL2:
.LBB8:
	.loc 1 20 32 is_stmt 1 discriminator 1 view .LVU7
	.loc 1 20 54 is_stmt 0 discriminator 3 view .LVU8
	movl	$17, %ecx
	leaq	32(%rsp), %rdx
.LBE8:
	.loc 1 17 18 discriminator 2 view .LVU9
	movdqu	.LC0(%rip), %xmm0
.LBB9:
	.loc 1 20 54 discriminator 3 view .LVU10
	movd	%ecx, %xmm3
	.loc 1 20 32 discriminator 1 view .LVU11
	movl	$4, %ecx
.LBE9:
	.loc 1 17 18 discriminator 2 view .LVU12
	movq	%rdx, %rax
.LBB10:
	.loc 1 20 32 discriminator 1 view .LVU13
	movd	%ecx, %xmm2
	.loc 1 20 54 discriminator 3 view .LVU14
	pshufd	$0, %xmm3, %xmm3
	.loc 1 20 32 discriminator 1 view .LVU15
	pshufd	$0, %xmm2, %xmm2
.LVL3:
	.loc 1 20 32 discriminator 1 view .LVU16
	.p2align 6
	.p2align 4
	.p2align 3
.L4:
	.loc 1 20 42 is_stmt 1 discriminator 3 view .LVU17
	.loc 1 20 54 is_stmt 0 discriminator 3 view .LVU18
	movdqa	%xmm0, %xmm1
	addq	$16, %rax
	leaq	65568(%rsp), %rcx
	paddd	%xmm3, %xmm1
	.loc 1 20 32 discriminator 1 view .LVU19
	paddd	%xmm2, %xmm0
	.loc 1 20 50 discriminator 3 view .LVU20
	movups	%xmm1, -16(%rax)
	.loc 1 20 37 is_stmt 1 discriminator 3 view .LVU21
	.loc 1 20 32 discriminator 1 view .LVU22
	cmpq	%rax, %rcx
	jne	.L4
.LVL4:
	.loc 1 20 32 is_stmt 0 discriminator 1 view .LVU23
.LBE10:
.LBB11:
	.loc 1 21 32 is_stmt 1 discriminator 1 view .LVU24
	testl	%r9d, %r9d
	je	.L5
	xorl	%r10d, %r10d
	cmpl	$2, %r9d
	jbe	.L7
	leal	-3(%r9), %r8d
.LBB12:
.LBB13:
.LBB14:
	.loc 1 11 25 is_stmt 0 view .LVU25
	movdqu	.LC3(%rip), %xmm2
.LBE14:
.LBE13:
.LBE12:
	.loc 1 21 23 view .LVU26
	xorl	%ecx, %ecx
	andl	$-2, %r8d
	leal	2(%r8), %r10d
.LVL5:
.L9:
.LBB23:
	.loc 1 22 36 is_stmt 1 discriminator 1 view .LVU27
.LBE23:
.LBE11:
	.loc 1 17 18 is_stmt 0 discriminator 2 view .LVU28
	movq	%rdx, %rax
.LVL6:
	.loc 1 17 18 discriminator 2 view .LVU29
	.p2align 6
	.p2align 4
	.p2align 3
.L8:
.LBB28:
.LBB24:
	.loc 1 23 13 is_stmt 1 view .LVU30
.LVL7:
.LBB19:
.LBI13:
	.loc 1 9 21 view .LVU31
.LBB15:
	.loc 1 11 5 view .LVU32
.LBE15:
.LBE19:
	.loc 1 22 41 discriminator 3 view .LVU33
.LBE24:
	.loc 1 21 42 discriminator 2 view .LVU34
	.loc 1 21 32 discriminator 1 view .LVU35
.LBB25:
	.loc 1 22 36 discriminator 1 view .LVU36
	.loc 1 23 13 view .LVU37
.LBB20:
	.loc 1 9 21 view .LVU38
.LBB16:
	.loc 1 11 5 view .LVU39
	.loc 1 11 19 is_stmt 0 view .LVU40
	movdqu	(%rax), %xmm1
	leaq	65568(%rsp), %rbx
	addq	$16, %rax
	movdqa	%xmm1, %xmm0
	pslld	$1, %xmm0
	paddd	%xmm1, %xmm0
	.loc 1 11 25 view .LVU41
	pxor	%xmm2, %xmm0
	.loc 1 11 19 view .LVU42
	movdqa	%xmm0, %xmm1
	pslld	$1, %xmm1
	paddd	%xmm1, %xmm0
	.loc 1 11 25 view .LVU43
	pxor	%xmm2, %xmm0
.LBE16:
.LBE20:
	.loc 1 23 21 discriminator 1 view .LVU44
	movups	%xmm0, -16(%rax)
	.loc 1 22 41 is_stmt 1 discriminator 3 view .LVU45
	.loc 1 22 36 discriminator 1 view .LVU46
	cmpq	%rbx, %rax
	jne	.L8
.LBE25:
	.loc 1 21 42 discriminator 2 view .LVU47
.LVL8:
	.loc 1 21 32 discriminator 1 view .LVU48
	cmpl	%ecx, %r8d
	je	.L7
	.loc 1 21 42 is_stmt 0 discriminator 2 view .LVU49
	addl	$2, %ecx
.LVL9:
	.loc 1 21 42 discriminator 2 view .LVU50
	jmp	.L9
.LVL10:
.L7:
.LBB26:
.LBB21:
.LBB17:
	.loc 1 11 25 view .LVU51
	movl	$-1640531527, %eax
	movd	%eax, %xmm2
	pshufd	$0, %xmm2, %xmm2
.LVL11:
.L11:
	.loc 1 11 25 view .LVU52
.LBE17:
.LBE21:
	.loc 1 22 36 is_stmt 1 discriminator 1 view .LVU53
.LBE26:
	.loc 1 21 32 is_stmt 0 discriminator 1 view .LVU54
	movq	%rdx, %rax
.LVL12:
	.loc 1 21 32 discriminator 1 view .LVU55
	.p2align 6
	.p2align 4
	.p2align 3
.L10:
.LBB27:
	.loc 1 23 13 is_stmt 1 view .LVU56
.LBB22:
	.loc 1 9 21 view .LVU57
.LBB18:
	.loc 1 11 5 view .LVU58
	.loc 1 11 19 is_stmt 0 view .LVU59
	movdqu	(%rax), %xmm1
	leaq	65568(%rsp), %rsi
	addq	$16, %rax
	movdqa	%xmm1, %xmm0
	pslld	$1, %xmm0
	paddd	%xmm1, %xmm0
	.loc 1 11 25 view .LVU60
	pxor	%xmm2, %xmm0
.LBE18:
.LBE22:
	.loc 1 23 21 discriminator 1 view .LVU61
	movups	%xmm0, -16(%rax)
	.loc 1 22 41 is_stmt 1 discriminator 3 view .LVU62
	.loc 1 22 36 discriminator 1 view .LVU63
	cmpq	%rax, %rsi
	jne	.L10
.LBE27:
	.loc 1 21 42 discriminator 2 view .LVU64
	addl	$1, %r10d
.LVL13:
	.loc 1 21 32 discriminator 1 view .LVU65
	cmpl	%r9d, %r10d
	jb	.L11
.LVL14:
.L5:
	.loc 1 21 32 is_stmt 0 discriminator 1 view .LVU66
.LBE28:
.LBB29:
	.loc 1 26 32 is_stmt 1 discriminator 1 view .LVU67
	leaq	65568(%rsp), %rax
.LBE29:
.LBB30:
	.loc 1 21 42 is_stmt 0 discriminator 2 view .LVU68
	pxor	%xmm0, %xmm0
	subq	%rdx, %rax
	testb	$16, %al
	je	.L12
.LVL15:
	.loc 1 21 42 discriminator 2 view .LVU69
.LBE30:
.LBB31:
	.loc 1 26 42 is_stmt 1 discriminator 3 view .LVU70
	.loc 1 26 51 is_stmt 0 discriminator 3 view .LVU71
	movdqu	(%rdx), %xmm0
	.loc 1 26 37 is_stmt 1 discriminator 3 view .LVU72
	.loc 1 26 32 discriminator 1 view .LVU73
	leaq	65568(%rsp), %rax
	addq	$16, %rdx
	cmpq	%rdx, %rax
	je	.L29
	.p2align 5
	.p2align 4
	.p2align 3
.L12:
	.loc 1 26 42 discriminator 3 view .LVU74
	.loc 1 26 51 is_stmt 0 discriminator 3 view .LVU75
	pxor	(%rdx), %xmm0
	.loc 1 26 37 is_stmt 1 discriminator 3 view .LVU76
	.loc 1 26 32 discriminator 1 view .LVU77
	.loc 1 26 42 discriminator 3 view .LVU78
	leaq	65568(%rsp), %rax
	.loc 1 26 51 is_stmt 0 discriminator 3 view .LVU79
	pxor	16(%rdx), %xmm0
	.loc 1 26 37 is_stmt 1 discriminator 3 view .LVU80
	.loc 1 26 32 discriminator 1 view .LVU81
	addq	$32, %rdx
	cmpq	%rdx, %rax
	jne	.L12
.L29:
.LBE31:
	.loc 1 27 5 view .LVU82
	movdqa	%xmm0, %xmm1
	leaq	.LC4(%rip), %rcx
	psrldq	$8, %xmm1
	pxor	%xmm1, %xmm0
	movdqa	%xmm0, %xmm1
	psrldq	$4, %xmm1
	pxor	%xmm1, %xmm0
	movd	%xmm0, %edx
	call	__mingw_printf
.LVL16:
	.loc 1 28 5 view .LVU83
	.loc 1 28 12 is_stmt 0 view .LVU84
	xorl	%eax, %eax
.L1:
	.loc 1 29 1 view .LVU85
	addq	$65576, %rsp
	.cfi_remember_state
	.cfi_def_cfa_offset 24
	popq	%rbx
	.cfi_restore 3
	.cfi_def_cfa_offset 16
	popq	%rsi
	.cfi_restore 4
	.cfi_def_cfa_offset 8
	ret
.LVL17:
.L31:
	.cfi_restore_state
	.loc 1 17 52 discriminator 1 view .LVU86
	movq	8(%rbx), %rcx
	movl	$10, %r8d
	xorl	%edx, %edx
	call	strtoul
.LVL18:
	movl	%eax, %r9d
.LVL19:
	.loc 1 18 5 is_stmt 1 view .LVU87
	.loc 1 19 5 view .LVU88
	.loc 1 19 33 is_stmt 0 discriminator 1 view .LVU89
	movl	$2, %eax
.LVL20:
	.loc 1 19 8 view .LVU90
	cmpl	$10000, %r9d
	ja	.L1
	jmp	.L2
	.cfi_endproc
.LFE18:
	.seh_endproc
	.section .rdata,"dr"
	.align 16
.LC0:
	.long	0
	.long	1
	.long	2
	.long	3
	.align 16
.LC3:
	.long	-1640531527
	.long	-1640531527
	.long	-1640531527
	.long	-1640531527
	.text
.Letext0:
	.file 2 "C:/msys64/mingw64/include/stdio.h"
	.file 3 "C:/msys64/mingw64/include/stdlib.h"
	.section	.debug_info,"dr"
.Ldebug_info0:
	.long	0x312
	.word	0x5
	.byte	0x1
	.byte	0x8
	.secrel32	.Ldebug_abbrev0
	.uleb128 0x9
	.ascii "GNU C11 15.1.0 -mtune=generic -march=nocona -g -O3 -std=c11\0"
	.byte	0x1d
	.secrel32	.LASF0
	.secrel32	.LASF1
	.secrel32	.LLRL13
	.quad	0
	.secrel32	.Ldebug_line0
	.uleb128 0x1
	.byte	0x1
	.byte	0x6
	.ascii "char\0"
	.uleb128 0xa
	.long	0x62
	.uleb128 0x1
	.byte	0x8
	.byte	0x7
	.ascii "long long unsigned int\0"
	.uleb128 0x1
	.byte	0x8
	.byte	0x5
	.ascii "long long int\0"
	.uleb128 0x1
	.byte	0x2
	.byte	0x7
	.ascii "short unsigned int\0"
	.uleb128 0x1
	.byte	0x4
	.byte	0x5
	.ascii "int\0"
	.uleb128 0x1
	.byte	0x4
	.byte	0x5
	.ascii "long int\0"
	.uleb128 0x4
	.long	0x62
	.uleb128 0x1
	.byte	0x4
	.byte	0x7
	.ascii "unsigned int\0"
	.uleb128 0x1
	.byte	0x4
	.byte	0x7
	.ascii "long unsigned int\0"
	.uleb128 0x1
	.byte	0x1
	.byte	0x8
	.ascii "unsigned char\0"
	.uleb128 0x1
	.byte	0x8
	.byte	0x4
	.ascii "double\0"
	.uleb128 0x1
	.byte	0x4
	.byte	0x4
	.ascii "float\0"
	.uleb128 0x1
	.byte	0x10
	.byte	0x4
	.ascii "long double\0"
	.uleb128 0xb
	.ascii "printf\0"
	.byte	0x2
	.word	0x15e
	.byte	0x5
	.ascii "__mingw_printf\0"
	.long	0xb0
	.long	0x14a
	.uleb128 0x3
	.long	0x14a
	.uleb128 0xc
	.byte	0
	.uleb128 0x4
	.long	0x6a
	.uleb128 0x7
	.long	0x14a
	.uleb128 0xd
	.ascii "strtoul\0"
	.byte	0x3
	.word	0x198
	.byte	0x19
	.long	0xd8
	.long	0x179
	.uleb128 0x3
	.long	0x14f
	.uleb128 0x3
	.long	0x17e
	.uleb128 0x3
	.long	0xb0
	.byte	0
	.uleb128 0x4
	.long	0xc3
	.uleb128 0x7
	.long	0x179
	.uleb128 0xe
	.ascii "main\0"
	.byte	0x1
	.byte	0xe
	.byte	0x5
	.long	0xb0
	.quad	.LFB18
	.quad	.LFE18-.LFB18
	.uleb128 0x1
	.byte	0x9c
	.long	0x2d4
	.uleb128 0x8
	.ascii "argc\0"
	.byte	0xe
	.long	0xb0
	.secrel32	.LLST0
	.secrel32	.LVUS0
	.uleb128 0x8
	.ascii "argv\0"
	.byte	0x1b
	.long	0x179
	.secrel32	.LLST1
	.secrel32	.LVUS1
	.uleb128 0xf
	.ascii "data\0"
	.byte	0x1
	.byte	0x10
	.byte	0x12
	.long	0x2d4
	.uleb128 0x4
	.byte	0x91
	.sleb128 -65568
	.uleb128 0x2
	.ascii "rounds\0"
	.byte	0x11
	.byte	0x12
	.long	0xc8
	.secrel32	.LLST2
	.secrel32	.LVUS2
	.uleb128 0x2
	.ascii "checksum\0"
	.byte	0x12
	.byte	0x12
	.long	0xc8
	.secrel32	.LLST3
	.secrel32	.LVUS3
	.uleb128 0x5
	.secrel32	.LLRL4
	.long	0x227
	.uleb128 0x2
	.ascii "i\0"
	.byte	0x14
	.byte	0x17
	.long	0xc8
	.secrel32	.LLST5
	.secrel32	.LVUS5
	.byte	0
	.uleb128 0x5
	.secrel32	.LLRL6
	.long	0x274
	.uleb128 0x2
	.ascii "r\0"
	.byte	0x15
	.byte	0x17
	.long	0xc8
	.secrel32	.LLST7
	.secrel32	.LVUS7
	.uleb128 0x10
	.secrel32	.LLRL8
	.uleb128 0x2
	.ascii "i\0"
	.byte	0x16
	.byte	0x1b
	.long	0xc8
	.secrel32	.LLST9
	.secrel32	.LVUS9
	.uleb128 0x11
	.long	0x2e5
	.quad	.LBI13
	.byte	.LVU31
	.secrel32	.LLRL10
	.byte	0x1
	.byte	0x17
	.byte	0x17
	.uleb128 0x12
	.long	0x2f7
	.byte	0
	.byte	0
	.byte	0
	.uleb128 0x5
	.secrel32	.LLRL11
	.long	0x28f
	.uleb128 0x2
	.ascii "i\0"
	.byte	0x1a
	.byte	0x17
	.long	0xc8
	.secrel32	.LLST12
	.secrel32	.LVUS12
	.byte	0
	.uleb128 0x13
	.quad	.LVL1
	.long	0x306
	.uleb128 0x14
	.quad	.LVL16
	.long	0x120
	.long	0x2bb
	.uleb128 0x6
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x9
	.byte	0x3
	.quad	.LC4
	.byte	0
	.uleb128 0x15
	.quad	.LVL18
	.long	0x154
	.uleb128 0x6
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x1
	.byte	0x30
	.uleb128 0x6
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1
	.byte	0x3a
	.byte	0
	.byte	0
	.uleb128 0x16
	.long	0xc8
	.long	0x2e5
	.uleb128 0x17
	.long	0x6f
	.word	0x3fff
	.byte	0
	.uleb128 0x18
	.ascii "step\0"
	.byte	0x1
	.byte	0x9
	.byte	0x15
	.long	0xc8
	.byte	0x1
	.long	0x306
	.uleb128 0x19
	.ascii "value\0"
	.byte	0x1
	.byte	0x9
	.byte	0x27
	.long	0xc8
	.byte	0
	.uleb128 0x1a
	.ascii "__main\0"
	.ascii "__main\0"
	.byte	0
	.section	.debug_abbrev,"dr"
.Ldebug_abbrev0:
	.uleb128 0x1
	.uleb128 0x24
	.byte	0
	.uleb128 0xb
	.uleb128 0xb
	.uleb128 0x3e
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0x8
	.byte	0
	.byte	0
	.uleb128 0x2
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 1
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.uleb128 0x2137
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x3
	.uleb128 0x5
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x4
	.uleb128 0xf
	.byte	0
	.uleb128 0xb
	.uleb128 0x21
	.sleb128 8
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x5
	.uleb128 0xb
	.byte	0x1
	.uleb128 0x55
	.uleb128 0x17
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x6
	.uleb128 0x49
	.byte	0
	.uleb128 0x2
	.uleb128 0x18
	.uleb128 0x7e
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x7
	.uleb128 0x37
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x8
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0x21
	.sleb128 1
	.uleb128 0x3b
	.uleb128 0x21
	.sleb128 14
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x17
	.uleb128 0x2137
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x9
	.uleb128 0x11
	.byte	0x1
	.uleb128 0x25
	.uleb128 0x8
	.uleb128 0x13
	.uleb128 0xb
	.uleb128 0x3
	.uleb128 0x1f
	.uleb128 0x1b
	.uleb128 0x1f
	.uleb128 0x55
	.uleb128 0x17
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x10
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0xa
	.uleb128 0x26
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xb
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x6e
	.uleb128 0x8
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x3c
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xc
	.uleb128 0x18
	.byte	0
	.byte	0
	.byte	0
	.uleb128 0xd
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0x5
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x3c
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xe
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x11
	.uleb128 0x1
	.uleb128 0x12
	.uleb128 0x7
	.uleb128 0x40
	.uleb128 0x18
	.uleb128 0x7a
	.uleb128 0x19
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xf
	.uleb128 0x34
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x10
	.uleb128 0xb
	.byte	0x1
	.uleb128 0x55
	.uleb128 0x17
	.byte	0
	.byte	0
	.uleb128 0x11
	.uleb128 0x1d
	.byte	0x1
	.uleb128 0x31
	.uleb128 0x13
	.uleb128 0x52
	.uleb128 0x1
	.uleb128 0x2138
	.uleb128 0xb
	.uleb128 0x55
	.uleb128 0x17
	.uleb128 0x58
	.uleb128 0xb
	.uleb128 0x59
	.uleb128 0xb
	.uleb128 0x57
	.uleb128 0xb
	.byte	0
	.byte	0
	.uleb128 0x12
	.uleb128 0x5
	.byte	0
	.uleb128 0x31
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x13
	.uleb128 0x48
	.byte	0
	.uleb128 0x7d
	.uleb128 0x1
	.uleb128 0x7f
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x14
	.uleb128 0x48
	.byte	0x1
	.uleb128 0x7d
	.uleb128 0x1
	.uleb128 0x7f
	.uleb128 0x13
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x15
	.uleb128 0x48
	.byte	0x1
	.uleb128 0x7d
	.uleb128 0x1
	.uleb128 0x7f
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x16
	.uleb128 0x1
	.byte	0x1
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x17
	.uleb128 0x21
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2f
	.uleb128 0x5
	.byte	0
	.byte	0
	.uleb128 0x18
	.uleb128 0x2e
	.byte	0x1
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x27
	.uleb128 0x19
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x20
	.uleb128 0xb
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x19
	.uleb128 0x5
	.byte	0
	.uleb128 0x3
	.uleb128 0x8
	.uleb128 0x3a
	.uleb128 0xb
	.uleb128 0x3b
	.uleb128 0xb
	.uleb128 0x39
	.uleb128 0xb
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x1a
	.uleb128 0x2e
	.byte	0
	.uleb128 0x3f
	.uleb128 0x19
	.uleb128 0x3c
	.uleb128 0x19
	.uleb128 0x6e
	.uleb128 0x8
	.uleb128 0x3
	.uleb128 0x8
	.byte	0
	.byte	0
	.byte	0
	.section	.debug_loclists,"dr"
	.long	.Ldebug_loc3-.Ldebug_loc2
.Ldebug_loc2:
	.word	0x5
	.byte	0x8
	.byte	0
	.long	0
.Ldebug_loc0:
.LVUS0:
	.uleb128 0
	.uleb128 .LVU3
	.uleb128 .LVU3
	.uleb128 .LVU52
	.uleb128 .LVU52
	.uleb128 .LVU86
	.uleb128 .LVU86
	.uleb128 0
.LLST0:
	.byte	0x6
	.quad	.LVL0
	.byte	0x4
	.uleb128 .LVL0-.LVL0
	.uleb128 .LVL1-1-.LVL0
	.uleb128 0x1
	.byte	0x52
	.byte	0x4
	.uleb128 .LVL1-1-.LVL0
	.uleb128 .LVL11-.LVL0
	.uleb128 0x1
	.byte	0x54
	.byte	0x4
	.uleb128 .LVL11-.LVL0
	.uleb128 .LVL17-.LVL0
	.uleb128 0x4
	.byte	0xa3
	.uleb128 0x1
	.byte	0x52
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL17-.LVL0
	.uleb128 .LFE18-.LVL0
	.uleb128 0x1
	.byte	0x54
	.byte	0
.LVUS1:
	.uleb128 0
	.uleb128 .LVU3
	.uleb128 .LVU3
	.uleb128 .LVU27
	.uleb128 .LVU27
	.uleb128 .LVU86
	.uleb128 .LVU86
	.uleb128 0
.LLST1:
	.byte	0x6
	.quad	.LVL0
	.byte	0x4
	.uleb128 .LVL0-.LVL0
	.uleb128 .LVL1-1-.LVL0
	.uleb128 0x1
	.byte	0x51
	.byte	0x4
	.uleb128 .LVL1-1-.LVL0
	.uleb128 .LVL5-.LVL0
	.uleb128 0x1
	.byte	0x53
	.byte	0x4
	.uleb128 .LVL5-.LVL0
	.uleb128 .LVL17-.LVL0
	.uleb128 0x4
	.byte	0xa3
	.uleb128 0x1
	.byte	0x51
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL17-.LVL0
	.uleb128 .LFE18-.LVL0
	.uleb128 0x1
	.byte	0x53
	.byte	0
.LVUS2:
	.uleb128 .LVU87
	.uleb128 .LVU90
	.uleb128 .LVU90
	.uleb128 0
.LLST2:
	.byte	0x6
	.quad	.LVL19
	.byte	0x4
	.uleb128 .LVL19-.LVL19
	.uleb128 .LVL20-.LVL19
	.uleb128 0x1
	.byte	0x50
	.byte	0x4
	.uleb128 .LVL20-.LVL19
	.uleb128 .LFE18-.LVL19
	.uleb128 0x1
	.byte	0x59
	.byte	0
.LVUS3:
	.uleb128 .LVU66
	.uleb128 .LVU69
	.uleb128 .LVU88
	.uleb128 0
.LLST3:
	.byte	0x6
	.quad	.LVL14
	.byte	0x4
	.uleb128 .LVL14-.LVL14
	.uleb128 .LVL15-.LVL14
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL19-.LVL14
	.uleb128 .LFE18-.LVL14
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0
.LVUS5:
	.uleb128 .LVU7
	.uleb128 .LVU16
.LLST5:
	.byte	0x8
	.quad	.LVL2
	.uleb128 .LVL3-.LVL2
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0
.LVUS7:
	.uleb128 .LVU23
	.uleb128 .LVU27
	.uleb128 .LVU27
	.uleb128 .LVU29
	.uleb128 .LVU48
	.uleb128 .LVU50
	.uleb128 .LVU50
	.uleb128 .LVU51
	.uleb128 .LVU52
	.uleb128 .LVU66
.LLST7:
	.byte	0x6
	.quad	.LVL4
	.byte	0x4
	.uleb128 .LVL4-.LVL4
	.uleb128 .LVL5-.LVL4
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL5-.LVL4
	.uleb128 .LVL6-.LVL4
	.uleb128 0x1
	.byte	0x52
	.byte	0x4
	.uleb128 .LVL8-.LVL4
	.uleb128 .LVL9-.LVL4
	.uleb128 0x3
	.byte	0x72
	.sleb128 2
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL9-.LVL4
	.uleb128 .LVL10-.LVL4
	.uleb128 0x1
	.byte	0x52
	.byte	0x4
	.uleb128 .LVL11-.LVL4
	.uleb128 .LVL14-.LVL4
	.uleb128 0x1
	.byte	0x5a
	.byte	0
.LVUS9:
	.uleb128 .LVU27
	.uleb128 .LVU29
	.uleb128 .LVU52
	.uleb128 .LVU55
.LLST9:
	.byte	0x6
	.quad	.LVL5
	.byte	0x4
	.uleb128 .LVL5-.LVL5
	.uleb128 .LVL6-.LVL5
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL11-.LVL5
	.uleb128 .LVL12-.LVL5
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0
.LVUS12:
	.uleb128 .LVU66
	.uleb128 .LVU69
.LLST12:
	.byte	0x8
	.quad	.LVL14
	.uleb128 .LVL15-.LVL14
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0
.Ldebug_loc3:
	.section	.debug_aranges,"dr"
	.long	0x2c
	.word	0x2
	.secrel32	.Ldebug_info0
	.byte	0x8
	.byte	0
	.word	0
	.word	0
	.quad	.LFB18
	.quad	.LFE18-.LFB18
	.quad	0
	.quad	0
	.section	.debug_rnglists,"dr"
.Ldebug_ranges0:
	.long	.Ldebug_ranges3-.Ldebug_ranges2
.Ldebug_ranges2:
	.word	0x5
	.byte	0x8
	.byte	0
	.long	0
.LLRL4:
	.byte	0x5
	.quad	.LBB8
	.byte	0x4
	.uleb128 .LBB8-.LBB8
	.uleb128 .LBE8-.LBB8
	.byte	0x4
	.uleb128 .LBB9-.LBB8
	.uleb128 .LBE9-.LBB8
	.byte	0x4
	.uleb128 .LBB10-.LBB8
	.uleb128 .LBE10-.LBB8
	.byte	0
.LLRL6:
	.byte	0x5
	.quad	.LBB11
	.byte	0x4
	.uleb128 .LBB11-.LBB11
	.uleb128 .LBE11-.LBB11
	.byte	0x4
	.uleb128 .LBB28-.LBB11
	.uleb128 .LBE28-.LBB11
	.byte	0x4
	.uleb128 .LBB30-.LBB11
	.uleb128 .LBE30-.LBB11
	.byte	0
.LLRL8:
	.byte	0x5
	.quad	.LBB12
	.byte	0x4
	.uleb128 .LBB12-.LBB12
	.uleb128 .LBE12-.LBB12
	.byte	0x4
	.uleb128 .LBB23-.LBB12
	.uleb128 .LBE23-.LBB12
	.byte	0x4
	.uleb128 .LBB24-.LBB12
	.uleb128 .LBE24-.LBB12
	.byte	0x4
	.uleb128 .LBB25-.LBB12
	.uleb128 .LBE25-.LBB12
	.byte	0x4
	.uleb128 .LBB26-.LBB12
	.uleb128 .LBE26-.LBB12
	.byte	0x4
	.uleb128 .LBB27-.LBB12
	.uleb128 .LBE27-.LBB12
	.byte	0
.LLRL10:
	.byte	0x5
	.quad	.LBB13
	.byte	0x4
	.uleb128 .LBB13-.LBB13
	.uleb128 .LBE13-.LBB13
	.byte	0x4
	.uleb128 .LBB19-.LBB13
	.uleb128 .LBE19-.LBB13
	.byte	0x4
	.uleb128 .LBB20-.LBB13
	.uleb128 .LBE20-.LBB13
	.byte	0x4
	.uleb128 .LBB21-.LBB13
	.uleb128 .LBE21-.LBB13
	.byte	0x4
	.uleb128 .LBB22-.LBB13
	.uleb128 .LBE22-.LBB13
	.byte	0
.LLRL11:
	.byte	0x5
	.quad	.LBB29
	.byte	0x4
	.uleb128 .LBB29-.LBB29
	.uleb128 .LBE29-.LBB29
	.byte	0x4
	.uleb128 .LBB31-.LBB29
	.uleb128 .LBE31-.LBB29
	.byte	0
.LLRL13:
	.byte	0x7
	.quad	.LFB18
	.uleb128 .LFE18-.LFB18
	.byte	0
.Ldebug_ranges3:
	.section	.debug_line,"dr"
.Ldebug_line0:
	.section	.debug_str,"dr"
	.section	.debug_line_str,"dr"
.LASF0:
	.ascii "C:\\Users\\MOINAK\\Documents\\Codex\\2026-10-25\\in-x20\\outputs\\CS-202_Project-main\\.optilab\\runs\\81cf30fbd418459e98180219060b1f51\\candidate.c\0"
.LASF1:
	.ascii "C:\\Users\\MOINAK\\Documents\\Codex\\2026-10-25\\in-x20\\outputs\\CS-202_Project-main\\.optilab\\runs\\81cf30fbd418459e98180219060b1f51\0"
	.def	__main;	.scl	2;	.type	32;	.endef
	.ident	"GCC: (Rev7, Built by MSYS2 project) 15.1.0"
	.def	strtoul;	.scl	2;	.type	32;	.endef
