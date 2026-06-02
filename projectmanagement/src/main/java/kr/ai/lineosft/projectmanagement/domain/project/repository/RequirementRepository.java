package kr.ai.lineosft.projectmanagement.domain.project.repository;

import kr.ai.lineosft.projectmanagement.domain.project.entity.Requirement;
import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface RequirementRepository extends JpaRepository<Requirement, Long> {

    @Query("SELECT r FROM Requirement r LEFT JOIN FETCH r.author LEFT JOIN FETCH r.assignee LEFT JOIN FETCH r.category WHERE r.project.id = :projectId ORDER BY r.requirementCode ASC")
    List<Requirement> findByProjectIdWithRelations(@Param("projectId") Long projectId);

    @Query("SELECT r FROM Requirement r LEFT JOIN FETCH r.author LEFT JOIN FETCH r.assignee LEFT JOIN FETCH r.category WHERE r.id = :id")
    Optional<Requirement> findByIdWithRelations(@Param("id") Long id);

    @Query("SELECT r FROM Requirement r WHERE r.requirementCode = :requirementCode")
    Optional<Requirement> findByRequirementCode(@Param("requirementCode") String requirementCode);

    long countByStatusIn(List<RequirementStatus> statuses);
}
