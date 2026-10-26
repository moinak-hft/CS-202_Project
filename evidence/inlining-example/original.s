	.file	"original.c"
	.text
.Ltext0:
	.cfi_sections	.debug_frame
	.file 0 "C:/Users/MOINAK/Documents/Codex/2026-10-25/in-x20/outputs/CS-202_Project-main/.optilab/runs/81cf30fbd418459e98180219060b1f51" "C:/Users/MOINAK/Documents/Codex/2026-10-25/in-x20/outputs/CS-202_Project-main/.optilab/runs/81cf30fbd418459e98180219060b1f51/original.c"
	.p2align 4
	.def	step;	.scl	3;	.type	32;	.endef
	.seh_proc	step
step:
.LVL0:
.LFB17:
	.file 1 "C:/Users/MOINAK/Documents/Codex/2026-10-25/in-x20/outputs/CS-202_Project-main/.optilab/runs/81cf30fbd418459e98180219060b1f51/original.c"
	.loc 1 10 1 view -0
	.cfi_startproc
	.loc 1 10 1 is_stmt 0 view .LVU1
	.seh_endprologue
	.loc 1 11 5 is_stmt 1 view .LVU2
	.loc 1 11 19 is_stmt 0 view .LVU3
	leal	(%rcx,%rcx,2), %eax
	.loc 1 11 25 view .LVU4
	xorl	$-1640531527, %eax
	.loc 1 12 1 view .LVU5
	ret
	.cfi_endproc
.LFE17:
	.seh_endproc
	.section .rdata,"dr"
.LC3:
	.ascii "%u\12\0"
	.section	.text.startup,"x"
	.p2align 4
	.globl	main
	.def	main;	.scl	2;	.type	32;	.endef
	.seh_proc	main
main:
.LVL1:
.LFB18:
	.loc 1 15 1 is_stmt 1 view -0
	.cfi_startproc
	.loc 1 15 1 is_stmt 0 view .LVU7
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
	.loc 1 15 1 view .LVU8
	movl	%ecx, %esi
	movq	%rdx, %rbx
	call	__main
.LVL2:
	.loc 1 16 5 is_stmt 1 view .LVU9
	.loc 1 17 5 view .LVU10
	.loc 1 17 18 is_stmt 0 discriminator 2 view .LVU11
	movl	$400, %r11d
	.loc 1 17 76 view .LVU12
	cmpl	$1, %esi
	jg	.L32
.L4:
.LVL3:
.LBB2:
	.loc 1 20 32 is_stmt 1 discriminator 1 view .LVU13
	.loc 1 20 54 is_stmt 0 discriminator 3 view .LVU14
	movl	$17, %ebx
.LVL4:
	.loc 1 20 54 discriminator 3 view .LVU15
	leaq	32(%rsp), %r8
.LBE2:
	.loc 1 17 18 discriminator 2 view .LVU16
	movdqu	.LC0(%rip), %xmm0
.LBB3:
	.loc 1 20 54 discriminator 3 view .LVU17
	movd	%ebx, %xmm3
	.loc 1 20 32 discriminator 1 view .LVU18
	movl	$4, %ebx
.LBE3:
	.loc 1 17 18 discriminator 2 view .LVU19
	movq	%r8, %rax
.LBB4:
	.loc 1 20 32 discriminator 1 view .LVU20
	movd	%ebx, %xmm2
	.loc 1 20 54 discriminator 3 view .LVU21
	pshufd	$0, %xmm3, %xmm3
	.loc 1 20 32 discriminator 1 view .LVU22
	pshufd	$0, %xmm2, %xmm2
.LVL5:
	.loc 1 20 32 discriminator 1 view .LVU23
	.p2align 6
	.p2align 4
	.p2align 3
.L6:
	.loc 1 20 42 is_stmt 1 discriminator 3 view .LVU24
	.loc 1 20 54 is_stmt 0 discriminator 3 view .LVU25
	movdqa	%xmm0, %xmm1
	addq	$16, %rax
	leaq	65568(%rsp), %rsi
	paddd	%xmm3, %xmm1
	.loc 1 20 32 discriminator 1 view .LVU26
	paddd	%xmm2, %xmm0
	.loc 1 20 50 discriminator 3 view .LVU27
	movups	%xmm1, -16(%rax)
	.loc 1 20 37 is_stmt 1 discriminator 3 view .LVU28
	.loc 1 20 32 discriminator 1 view .LVU29
	cmpq	%rsi, %rax
	jne	.L6
.LVL6:
	.loc 1 20 32 is_stmt 0 discriminator 1 view .LVU30
.LBE4:
.LBB5:
	.loc 1 21 32 is_stmt 1 discriminator 1 view .LVU31
	testl	%r11d, %r11d
	je	.L7
	xorl	%ebx, %ebx
	cmpl	$2, %r11d
	jbe	.L13
	leal	-3(%r11), %r10d
	.loc 1 21 23 is_stmt 0 view .LVU32
	xorl	%r9d, %r9d
	andl	$-2, %r10d
	leal	2(%r10), %ebx
.LVL7:
.L11:
.LBB6:
	.loc 1 22 36 is_stmt 1 discriminator 1 view .LVU33
.LBE6:
.LBE5:
	.loc 1 17 18 is_stmt 0 discriminator 2 view .LVU34
	movq	%r8, %rdx
.LVL8:
	.p2align 4
	.p2align 3
.L10:
.LBB11:
.LBB7:
	.loc 1 23 13 is_stmt 1 view .LVU35
	.loc 1 23 23 is_stmt 0 view .LVU36
	movl	(%rdx), %ecx
	.loc 1 22 36 discriminator 1 view .LVU37
	addq	$4, %rdx
.LVL9:
	.loc 1 23 23 view .LVU38
	call	step
.LVL10:
	.loc 1 22 41 is_stmt 1 discriminator 3 view .LVU39
.LBE7:
	.loc 1 21 42 discriminator 2 view .LVU40
	.loc 1 21 32 discriminator 1 view .LVU41
.LBB8:
	.loc 1 22 36 discriminator 1 view .LVU42
	.loc 1 23 13 view .LVU43
	.loc 1 23 23 is_stmt 0 view .LVU44
	movl	%eax, %ecx
	call	step
.LVL11:
	.loc 1 23 21 discriminator 1 view .LVU45
	movl	%eax, -4(%rdx)
	.loc 1 22 41 is_stmt 1 discriminator 3 view .LVU46
.LVL12:
	.loc 1 22 36 discriminator 1 view .LVU47
	leaq	65568(%rsp), %rax
	cmpq	%rax, %rdx
	jne	.L10
.LBE8:
	.loc 1 21 42 discriminator 2 view .LVU48
.LVL13:
	.loc 1 21 32 discriminator 1 view .LVU49
	cmpl	%r10d, %r9d
	je	.L13
	.loc 1 21 42 is_stmt 0 discriminator 2 view .LVU50
	addl	$2, %r9d
.LVL14:
	.loc 1 21 42 discriminator 2 view .LVU51
	jmp	.L11
.LVL15:
.L13:
.LBB9:
	.loc 1 22 36 is_stmt 1 discriminator 1 view .LVU52
.LBE9:
	.loc 1 21 32 is_stmt 0 discriminator 1 view .LVU53
	movq	%r8, %rdx
.LVL16:
	.p2align 4
	.p2align 3
.L12:
.LBB10:
	.loc 1 23 13 is_stmt 1 view .LVU54
	.loc 1 23 23 is_stmt 0 view .LVU55
	movl	(%rdx), %ecx
	.loc 1 22 36 discriminator 1 view .LVU56
	addq	$4, %rdx
.LVL17:
	.loc 1 23 23 view .LVU57
	call	step
.LVL18:
	.loc 1 23 21 discriminator 1 view .LVU58
	movl	%eax, -4(%rdx)
	.loc 1 22 41 is_stmt 1 discriminator 3 view .LVU59
.LVL19:
	.loc 1 22 36 discriminator 1 view .LVU60
	leaq	65568(%rsp), %rax
	cmpq	%rax, %rdx
	jne	.L12
.LBE10:
	.loc 1 21 42 discriminator 2 view .LVU61
	addl	$1, %ebx
.LVL20:
	.loc 1 21 32 discriminator 1 view .LVU62
	cmpl	%r11d, %ebx
	jb	.L13
.LVL21:
.L7:
	.loc 1 21 32 is_stmt 0 discriminator 1 view .LVU63
.LBE11:
.LBB12:
	.loc 1 26 32 is_stmt 1 discriminator 1 view .LVU64
	leaq	65568(%rsp), %rax
.LBE12:
.LBB13:
	.loc 1 21 42 is_stmt 0 discriminator 2 view .LVU65
	pxor	%xmm0, %xmm0
	subq	%r8, %rax
	testb	$16, %al
	je	.L14
.LVL22:
	.loc 1 21 42 discriminator 2 view .LVU66
.LBE13:
.LBB14:
	.loc 1 26 42 is_stmt 1 discriminator 3 view .LVU67
	.loc 1 26 51 is_stmt 0 discriminator 3 view .LVU68
	movdqu	(%r8), %xmm0
	.loc 1 26 37 is_stmt 1 discriminator 3 view .LVU69
	.loc 1 26 32 discriminator 1 view .LVU70
	leaq	65568(%rsp), %rax
	addq	$16, %r8
	cmpq	%rax, %r8
	je	.L31
	.p2align 5
	.p2align 4
	.p2align 3
.L14:
	.loc 1 26 42 discriminator 3 view .LVU71
	.loc 1 26 51 is_stmt 0 discriminator 3 view .LVU72
	pxor	(%r8), %xmm0
	.loc 1 26 37 is_stmt 1 discriminator 3 view .LVU73
	.loc 1 26 32 discriminator 1 view .LVU74
	.loc 1 26 42 discriminator 3 view .LVU75
	leaq	65568(%rsp), %rax
	.loc 1 26 51 is_stmt 0 discriminator 3 view .LVU76
	pxor	16(%r8), %xmm0
	.loc 1 26 37 is_stmt 1 discriminator 3 view .LVU77
	.loc 1 26 32 discriminator 1 view .LVU78
	addq	$32, %r8
	cmpq	%rax, %r8
	jne	.L14
.L31:
.LBE14:
	.loc 1 27 5 view .LVU79
	movdqa	%xmm0, %xmm1
	leaq	.LC3(%rip), %rcx
	psrldq	$8, %xmm1
	pxor	%xmm1, %xmm0
	movdqa	%xmm0, %xmm1
	psrldq	$4, %xmm1
	pxor	%xmm1, %xmm0
	movd	%xmm0, %edx
	call	__mingw_printf
.LVL23:
	.loc 1 28 5 view .LVU80
	.loc 1 28 12 is_stmt 0 view .LVU81
	xorl	%eax, %eax
.L3:
	.loc 1 29 1 view .LVU82
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
.LVL24:
.L32:
	.cfi_restore_state
	.loc 1 17 52 discriminator 1 view .LVU83
	movq	8(%rbx), %rcx
	movl	$10, %r8d
	xorl	%edx, %edx
	call	strtoul
.LVL25:
	movl	%eax, %r11d
.LVL26:
	.loc 1 18 5 is_stmt 1 view .LVU84
	.loc 1 19 5 view .LVU85
	.loc 1 19 33 is_stmt 0 discriminator 1 view .LVU86
	movl	$2, %eax
.LVL27:
	.loc 1 19 8 view .LVU87
	cmpl	$10000, %r11d
	ja	.L3
	jmp	.L4
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
	.text
.Letext0:
	.file 2 "C:/msys64/mingw64/include/stdio.h"
	.file 3 "C:/msys64/mingw64/include/stdlib.h"
	.section	.debug_info,"dr"
.Ldebug_info0:
	.long	0x34e
	.word	0x5
	.byte	0x1
	.byte	0x8
	.secrel32	.Ldebug_abbrev0
	.uleb128 0xb
	.ascii "GNU C11 15.1.0 -mtune=generic -march=nocona -g -O3 -std=c11\0"
	.byte	0x1d
	.secrel32	.LASF0
	.secrel32	.LASF1
	.secrel32	.LLRL12
	.quad	0
	.secrel32	.Ldebug_line0
	.uleb128 0x1
	.byte	0x1
	.byte	0x6
	.ascii "char\0"
	.uleb128 0xc
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
	.uleb128 0x5
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
	.uleb128 0xd
	.ascii "printf\0"
	.byte	0x2
	.word	0x15e
	.byte	0x5
	.ascii "__mingw_printf\0"
	.long	0xb0
	.long	0x14a
	.uleb128 0x4
	.long	0x14a
	.uleb128 0xe
	.byte	0
	.uleb128 0x5
	.long	0x6a
	.uleb128 0x8
	.long	0x14a
	.uleb128 0xf
	.ascii "strtoul\0"
	.byte	0x3
	.word	0x198
	.byte	0x19
	.long	0xd8
	.long	0x179
	.uleb128 0x4
	.long	0x14f
	.uleb128 0x4
	.long	0x17e
	.uleb128 0x4
	.long	0xb0
	.byte	0
	.uleb128 0x5
	.long	0xc3
	.uleb128 0x8
	.long	0x179
	.uleb128 0x10
	.ascii "main\0"
	.byte	0x1
	.byte	0xe
	.byte	0x5
	.long	0xb0
	.quad	.LFB18
	.quad	.LFE18-.LFB18
	.uleb128 0x1
	.byte	0x9c
	.long	0x2fd
	.uleb128 0x9
	.ascii "argc\0"
	.byte	0xe
	.long	0xb0
	.secrel32	.LLST0
	.secrel32	.LVUS0
	.uleb128 0x9
	.ascii "argv\0"
	.byte	0x1b
	.long	0x179
	.secrel32	.LLST1
	.secrel32	.LVUS1
	.uleb128 0x11
	.ascii "data\0"
	.byte	0x1
	.byte	0x10
	.byte	0x12
	.long	0x2fd
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
	.uleb128 0x6
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
	.uleb128 0x6
	.secrel32	.LLRL6
	.long	0x29d
	.uleb128 0x2
	.ascii "r\0"
	.byte	0x15
	.byte	0x17
	.long	0xc8
	.secrel32	.LLST7
	.secrel32	.LVUS7
	.uleb128 0x12
	.secrel32	.LLRL8
	.uleb128 0x2
	.ascii "i\0"
	.byte	0x16
	.byte	0x1b
	.long	0xc8
	.secrel32	.LLST9
	.secrel32	.LVUS9
	.uleb128 0x7
	.quad	.LVL10
	.long	0x30e
	.long	0x26f
	.uleb128 0x3
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x2
	.byte	0x72
	.sleb128 0
	.byte	0
	.uleb128 0x7
	.quad	.LVL11
	.long	0x30e
	.long	0x287
	.uleb128 0x3
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x2
	.byte	0x72
	.sleb128 0
	.byte	0
	.uleb128 0xa
	.quad	.LVL18
	.long	0x30e
	.uleb128 0x3
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x2
	.byte	0x72
	.sleb128 0
	.byte	0
	.byte	0
	.byte	0
	.uleb128 0x6
	.secrel32	.LLRL10
	.long	0x2b8
	.uleb128 0x2
	.ascii "i\0"
	.byte	0x1a
	.byte	0x17
	.long	0xc8
	.secrel32	.LLST11
	.secrel32	.LVUS11
	.byte	0
	.uleb128 0x13
	.quad	.LVL2
	.long	0x342
	.uleb128 0x7
	.quad	.LVL23
	.long	0x120
	.long	0x2e4
	.uleb128 0x3
	.uleb128 0x1
	.byte	0x52
	.uleb128 0x9
	.byte	0x3
	.quad	.LC3
	.byte	0
	.uleb128 0xa
	.quad	.LVL25
	.long	0x154
	.uleb128 0x3
	.uleb128 0x1
	.byte	0x51
	.uleb128 0x1
	.byte	0x30
	.uleb128 0x3
	.uleb128 0x1
	.byte	0x58
	.uleb128 0x1
	.byte	0x3a
	.byte	0
	.byte	0
	.uleb128 0x14
	.long	0xc8
	.long	0x30e
	.uleb128 0x15
	.long	0x6f
	.word	0x3fff
	.byte	0
	.uleb128 0x16
	.ascii "step\0"
	.byte	0x1
	.byte	0x9
	.byte	0x15
	.long	0xc8
	.quad	.LFB17
	.quad	.LFE17-.LFB17
	.uleb128 0x1
	.byte	0x9c
	.long	0x342
	.uleb128 0x17
	.ascii "value\0"
	.byte	0x1
	.byte	0x9
	.byte	0x27
	.long	0xc8
	.uleb128 0x1
	.byte	0x52
	.byte	0
	.uleb128 0x18
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
	.uleb128 0x49
	.byte	0
	.uleb128 0x2
	.uleb128 0x18
	.uleb128 0x7e
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x4
	.uleb128 0x5
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x5
	.uleb128 0xf
	.byte	0
	.uleb128 0xb
	.uleb128 0x21
	.sleb128 8
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x6
	.uleb128 0xb
	.byte	0x1
	.uleb128 0x55
	.uleb128 0x17
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x7
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
	.uleb128 0x8
	.uleb128 0x37
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x9
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
	.uleb128 0xa
	.uleb128 0x48
	.byte	0x1
	.uleb128 0x7d
	.uleb128 0x1
	.uleb128 0x7f
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0xb
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
	.uleb128 0xc
	.uleb128 0x26
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
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
	.uleb128 0xe
	.uleb128 0x18
	.byte	0
	.byte	0
	.byte	0
	.uleb128 0xf
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
	.uleb128 0x10
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
	.uleb128 0x11
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
	.uleb128 0x12
	.uleb128 0xb
	.byte	0x1
	.uleb128 0x55
	.uleb128 0x17
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
	.uleb128 0x1
	.byte	0x1
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x1
	.uleb128 0x13
	.byte	0
	.byte	0
	.uleb128 0x15
	.uleb128 0x21
	.byte	0
	.uleb128 0x49
	.uleb128 0x13
	.uleb128 0x2f
	.uleb128 0x5
	.byte	0
	.byte	0
	.uleb128 0x16
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
	.uleb128 0x17
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
	.uleb128 0x2
	.uleb128 0x18
	.byte	0
	.byte	0
	.uleb128 0x18
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
	.uleb128 .LVU9
	.uleb128 .LVU9
	.uleb128 .LVU23
	.uleb128 .LVU23
	.uleb128 .LVU83
	.uleb128 .LVU83
	.uleb128 0
.LLST0:
	.byte	0x6
	.quad	.LVL1
	.byte	0x4
	.uleb128 .LVL1-.LVL1
	.uleb128 .LVL2-1-.LVL1
	.uleb128 0x1
	.byte	0x52
	.byte	0x4
	.uleb128 .LVL2-1-.LVL1
	.uleb128 .LVL5-.LVL1
	.uleb128 0x1
	.byte	0x54
	.byte	0x4
	.uleb128 .LVL5-.LVL1
	.uleb128 .LVL24-.LVL1
	.uleb128 0x4
	.byte	0xa3
	.uleb128 0x1
	.byte	0x52
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL24-.LVL1
	.uleb128 .LFE18-.LVL1
	.uleb128 0x1
	.byte	0x54
	.byte	0
.LVUS1:
	.uleb128 0
	.uleb128 .LVU9
	.uleb128 .LVU9
	.uleb128 .LVU15
	.uleb128 .LVU15
	.uleb128 .LVU83
	.uleb128 .LVU83
	.uleb128 0
.LLST1:
	.byte	0x6
	.quad	.LVL1
	.byte	0x4
	.uleb128 .LVL1-.LVL1
	.uleb128 .LVL2-1-.LVL1
	.uleb128 0x1
	.byte	0x51
	.byte	0x4
	.uleb128 .LVL2-1-.LVL1
	.uleb128 .LVL4-.LVL1
	.uleb128 0x1
	.byte	0x53
	.byte	0x4
	.uleb128 .LVL4-.LVL1
	.uleb128 .LVL24-.LVL1
	.uleb128 0x4
	.byte	0xa3
	.uleb128 0x1
	.byte	0x51
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL24-.LVL1
	.uleb128 .LFE18-.LVL1
	.uleb128 0x1
	.byte	0x53
	.byte	0
.LVUS2:
	.uleb128 .LVU84
	.uleb128 .LVU87
	.uleb128 .LVU87
	.uleb128 0
.LLST2:
	.byte	0x6
	.quad	.LVL26
	.byte	0x4
	.uleb128 .LVL26-.LVL26
	.uleb128 .LVL27-.LVL26
	.uleb128 0x1
	.byte	0x50
	.byte	0x4
	.uleb128 .LVL27-.LVL26
	.uleb128 .LFE18-.LVL26
	.uleb128 0x1
	.byte	0x5b
	.byte	0
.LVUS3:
	.uleb128 .LVU63
	.uleb128 .LVU66
	.uleb128 .LVU85
	.uleb128 0
.LLST3:
	.byte	0x6
	.quad	.LVL21
	.byte	0x4
	.uleb128 .LVL21-.LVL21
	.uleb128 .LVL22-.LVL21
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL26-.LVL21
	.uleb128 .LFE18-.LVL21
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0
.LVUS5:
	.uleb128 .LVU13
	.uleb128 .LVU23
.LLST5:
	.byte	0x8
	.quad	.LVL3
	.uleb128 .LVL5-.LVL3
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0
.LVUS7:
	.uleb128 .LVU30
	.uleb128 .LVU33
	.uleb128 .LVU33
	.uleb128 .LVU35
	.uleb128 .LVU49
	.uleb128 .LVU51
	.uleb128 .LVU51
	.uleb128 .LVU52
	.uleb128 .LVU52
	.uleb128 .LVU63
.LLST7:
	.byte	0x6
	.quad	.LVL6
	.byte	0x4
	.uleb128 .LVL6-.LVL6
	.uleb128 .LVL7-.LVL6
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL7-.LVL6
	.uleb128 .LVL8-.LVL6
	.uleb128 0x1
	.byte	0x59
	.byte	0x4
	.uleb128 .LVL13-.LVL6
	.uleb128 .LVL14-.LVL6
	.uleb128 0x3
	.byte	0x79
	.sleb128 2
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL14-.LVL6
	.uleb128 .LVL15-.LVL6
	.uleb128 0x1
	.byte	0x59
	.byte	0x4
	.uleb128 .LVL15-.LVL6
	.uleb128 .LVL21-.LVL6
	.uleb128 0x1
	.byte	0x53
	.byte	0
.LVUS9:
	.uleb128 .LVU33
	.uleb128 .LVU35
	.uleb128 .LVU35
	.uleb128 .LVU38
	.uleb128 .LVU38
	.uleb128 .LVU47
	.uleb128 .LVU52
	.uleb128 .LVU54
	.uleb128 .LVU54
	.uleb128 .LVU57
	.uleb128 .LVU57
	.uleb128 .LVU60
.LLST9:
	.byte	0x6
	.quad	.LVL7
	.byte	0x4
	.uleb128 .LVL7-.LVL7
	.uleb128 .LVL8-.LVL7
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL8-.LVL7
	.uleb128 .LVL9-.LVL7
	.uleb128 0xc
	.byte	0x71
	.sleb128 0
	.byte	0x91
	.sleb128 0
	.byte	0x1c
	.byte	0x23
	.uleb128 0x10020
	.byte	0x32
	.byte	0x25
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL9-.LVL7
	.uleb128 .LVL12-.LVL7
	.uleb128 0xc
	.byte	0x71
	.sleb128 0
	.byte	0x91
	.sleb128 0
	.byte	0x1c
	.byte	0x23
	.uleb128 0x1001c
	.byte	0x32
	.byte	0x25
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL15-.LVL7
	.uleb128 .LVL16-.LVL7
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL16-.LVL7
	.uleb128 .LVL17-.LVL7
	.uleb128 0xc
	.byte	0x71
	.sleb128 0
	.byte	0x91
	.sleb128 0
	.byte	0x1c
	.byte	0x23
	.uleb128 0x10020
	.byte	0x32
	.byte	0x25
	.byte	0x9f
	.byte	0x4
	.uleb128 .LVL17-.LVL7
	.uleb128 .LVL19-.LVL7
	.uleb128 0xc
	.byte	0x71
	.sleb128 0
	.byte	0x91
	.sleb128 0
	.byte	0x1c
	.byte	0x23
	.uleb128 0x1001c
	.byte	0x32
	.byte	0x25
	.byte	0x9f
	.byte	0
.LVUS11:
	.uleb128 .LVU63
	.uleb128 .LVU66
.LLST11:
	.byte	0x8
	.quad	.LVL21
	.uleb128 .LVL22-.LVL21
	.uleb128 0x2
	.byte	0x30
	.byte	0x9f
	.byte	0
.Ldebug_loc3:
	.section	.debug_aranges,"dr"
	.long	0x3c
	.word	0x2
	.secrel32	.Ldebug_info0
	.byte	0x8
	.byte	0
	.word	0
	.word	0
	.quad	.Ltext0
	.quad	.Letext0-.Ltext0
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
	.quad	.LBB2
	.byte	0x4
	.uleb128 .LBB2-.LBB2
	.uleb128 .LBE2-.LBB2
	.byte	0x4
	.uleb128 .LBB3-.LBB2
	.uleb128 .LBE3-.LBB2
	.byte	0x4
	.uleb128 .LBB4-.LBB2
	.uleb128 .LBE4-.LBB2
	.byte	0
.LLRL6:
	.byte	0x5
	.quad	.LBB5
	.byte	0x4
	.uleb128 .LBB5-.LBB5
	.uleb128 .LBE5-.LBB5
	.byte	0x4
	.uleb128 .LBB11-.LBB5
	.uleb128 .LBE11-.LBB5
	.byte	0x4
	.uleb128 .LBB13-.LBB5
	.uleb128 .LBE13-.LBB5
	.byte	0
.LLRL8:
	.byte	0x5
	.quad	.LBB6
	.byte	0x4
	.uleb128 .LBB6-.LBB6
	.uleb128 .LBE6-.LBB6
	.byte	0x4
	.uleb128 .LBB7-.LBB6
	.uleb128 .LBE7-.LBB6
	.byte	0x4
	.uleb128 .LBB8-.LBB6
	.uleb128 .LBE8-.LBB6
	.byte	0x4
	.uleb128 .LBB9-.LBB6
	.uleb128 .LBE9-.LBB6
	.byte	0x4
	.uleb128 .LBB10-.LBB6
	.uleb128 .LBE10-.LBB6
	.byte	0
.LLRL10:
	.byte	0x5
	.quad	.LBB12
	.byte	0x4
	.uleb128 .LBB12-.LBB12
	.uleb128 .LBE12-.LBB12
	.byte	0x4
	.uleb128 .LBB14-.LBB12
	.uleb128 .LBE14-.LBB12
	.byte	0
.LLRL12:
	.byte	0x7
	.quad	.Ltext0
	.uleb128 .Letext0-.Ltext0
	.byte	0x7
	.quad	.LFB18
	.uleb128 .LFE18-.LFB18
	.byte	0
.Ldebug_ranges3:
	.section	.debug_line,"dr"
.Ldebug_line0:
	.section	.debug_str,"dr"
	.section	.debug_line_str,"dr"
.LASF1:
	.ascii "C:\\Users\\MOINAK\\Documents\\Codex\\2026-10-25\\in-x20\\outputs\\CS-202_Project-main\\.optilab\\runs\\81cf30fbd418459e98180219060b1f51\0"
.LASF0:
	.ascii "C:\\Users\\MOINAK\\Documents\\Codex\\2026-10-25\\in-x20\\outputs\\CS-202_Project-main\\.optilab\\runs\\81cf30fbd418459e98180219060b1f51\\original.c\0"
	.def	__main;	.scl	2;	.type	32;	.endef
	.ident	"GCC: (Rev7, Built by MSYS2 project) 15.1.0"
	.def	strtoul;	.scl	2;	.type	32;	.endef
