package kr.ai.lineosft.projectmanagement.global.config;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class DatabaseSchemaPatcher {

    private final JdbcTemplate jdbcTemplate;

    @PostConstruct
    public void patchSchema() {
        try {
            log.info("Checking database schema to drop deprecated requirements.category column...");
            jdbcTemplate.execute("ALTER TABLE requirements DROP COLUMN IF EXISTS category");
            log.info("Deprecated requirements.category column dropped successfully.");
        } catch (Exception e) {
            log.warn("Failed to drop deprecated category column (it might have already been dropped): {}", e.getMessage());
        }
    }
}
