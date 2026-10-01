package com.example.demo.repository;

import com.example.demo.model.History;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.*;

public interface HistoryRepository extends JpaRepository<History, Long> {
	List<History> findByWorkerId(Long workerId);
}