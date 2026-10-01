package com.example.demo.controller;

import com.example.demo.service.HistoryService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/history")
public class HistoryController {
	private final HistoryService s;

	public HistoryController(HistoryService s) {
		this.s = s;
	}

	@GetMapping
	public Object all() {
		return s.all();
	}
}
