package com.example.demo.repository;

import com.example.demo.model.WorkerSession;
import org.springframework.data.jpa.repository.JpaRepository;
import java.time.*;
import java.util.*;

public interface WorkerSessionRepository extends JpaRepository<WorkerSession, Long> {
	Optional<WorkerSession> findFirstByWorkerIdAndLogoutTimeIsNullOrderByLoginTimeDesc(Long workerId);

	List<WorkerSession> findByWorkerIdAndSessionDateBetween(Long workerId, LocalDate from, LocalDate to);
}