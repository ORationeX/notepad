package kr.ai.lineosft.projectmanagement.domain.project.repository;

import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface RequirementHistoryRepository extends JpaRepository<RequirementHistory, Long> {

    @Query("SELECT h FROM RequirementHistory h LEFT JOIN FETCH h.category LEFT JOIN FETCH h.modifier WHERE h.requirement.id = :requirementId ORDER BY h.modifiedAt DESC")
    List<RequirementHistory> findByRequirementIdOrderByModifiedAtDesc(@Param("requirementId") Long requirementId);
}
