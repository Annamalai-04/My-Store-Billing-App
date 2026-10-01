package com.example.demo.controller;

import com.example.demo.dto.LoginRequest;
import com.example.demo.dto.WorkerRequest;
import com.example.demo.model.Worker;
import com.example.demo.model.WorkerSession;
import com.example.demo.service.WorkerService;
import com.example.demo.repository.WorkerRepository;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/workers")
public class WorkerController {

    private final WorkerService workerService;
    private final WorkerRepository workerRepository;

    public WorkerController(
            WorkerService workerService,
            WorkerRepository workerRepository) {
        this.workerService = workerService;
        this.workerRepository = workerRepository;
    }

    // =========================
    // ALL WORKERS
    // =========================

    @GetMapping
    public ResponseEntity<?> allWorkers() {
        try {
            List<Map<String, Object>> workers =
                    workerRepository.findAll()
                            .stream()
                            .map(worker -> Map.<String, Object>of(
                                    "workerId", worker.getWorkerId(),
                                    "name", worker.getName() == null
                                            ? ""
                                            : worker.getName(),
                                    "username", worker.getUsername() == null
                                            ? ""
                                            : worker.getUsername()
                            ))
                            .toList();

            return ResponseEntity.ok(workers);
        } catch (RuntimeException e) {
            return ResponseEntity
                    .badRequest()
                    .body(Map.of("message", e.getMessage()));
        }
    }

    // =========================
    // LOGIN
    // =========================

    @PostMapping("/login")
    public ResponseEntity<?> login(
            @RequestBody LoginRequest request) {

        try {

            Worker worker =
                    workerService.login(request);

            return ResponseEntity.ok(worker);

        } catch (RuntimeException e) {

            return ResponseEntity
                    .status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of(
                            "message",
                            e.getMessage()
                    ));
        }
    }

    // =========================
    // SIGNUP
    // =========================

    @PostMapping("/signup")
    public ResponseEntity<?> signup(
            @RequestBody WorkerRequest request) {

        try {

            Worker worker =
                    workerService.signup(request);

            return ResponseEntity.ok(worker);

        } catch (RuntimeException e) {

            return ResponseEntity
                    .badRequest()
                    .body(Map.of(
                            "message",
                            e.getMessage()
                    ));
        }
    }

    // =========================
    // UPDATE
    // =========================

    @PutMapping("/{id}")
    public ResponseEntity<?> update(
            @PathVariable Long id,
            @RequestBody WorkerRequest request) {

        try {

            Worker worker =
                    workerService.update(id, request);

            return ResponseEntity.ok(worker);

        } catch (RuntimeException e) {

            return ResponseEntity
                    .badRequest()
                    .body(Map.of(
                            "message",
                            e.getMessage()
                    ));
        }
    }

    // =========================
    // LOGOUT
    // =========================

    @PostMapping("/{id}/logout")
    public ResponseEntity<?> logout(
            @PathVariable Long id) {

        try {

            workerService.logout(id);

            return ResponseEntity.ok(
                    Map.of(
                            "message",
                            "Logout successful"
                    )
            );

        } catch (RuntimeException e) {

            return ResponseEntity
                    .badRequest()
                    .body(Map.of(
                            "message",
                            e.getMessage()
                    ));
        }
    }

    // =========================
    // WORKER SESSIONS
    // =========================

    @GetMapping("/{id}/sessions")
    public ResponseEntity<?> sessions(
            @PathVariable Long id,

            @RequestParam
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            LocalDate from,

            @RequestParam
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            LocalDate to) {

        try {

            List<WorkerSession> sessions =
                    workerService.sessions(
                            id,
                            from,
                            to
                    );

            return ResponseEntity.ok(sessions);

        } catch (RuntimeException e) {

            return ResponseEntity
                    .badRequest()
                    .body(Map.of(
                            "message",
                            e.getMessage()
                    ));
        }
    }
}